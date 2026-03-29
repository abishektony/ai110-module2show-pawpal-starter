from dataclasses import dataclass

from pawpal_system import DailyPlan, Owner, Pet, Task


@dataclass
class Scheduler:
    owner: Owner
    pet: Pet

    def schedule(self) -> DailyPlan:
        """Build and return a DailyPlan by fitting prioritized tasks into available time."""
        constraints = self.owner.get_constraints()
        available = constraints["available_minutes"]

        # Sort by time first (stable), then by priority — result is priority-ordered
        # with chronological order preserved as a tiebreaker within each priority group
        time_sorted = self.sort_by_time(self.pet.tasks)
        priority_sorted = self._sort_by_priority(time_sorted)
        filtered_tasks = self._filter_by_time(priority_sorted)

        scheduled = []
        skipped = []
        time_used = 0

        for task in filtered_tasks:
            if time_used + task.duration_minutes <= available:
                scheduled.append(task)
                time_used += task.duration_minutes
            else:
                skipped.append(task)

        reasoning = self.explain_plan(DailyPlan(scheduled, skipped, time_used))
        return DailyPlan(scheduled, skipped, time_used, reasoning)

    def fits_in_time(self, tasks: list[Task]) -> bool:
        """Return True if the combined duration of tasks fits within available time."""
        total = sum(t.duration_minutes for t in tasks)
        return total <= self.owner.available_minutes

    def explain_plan(self, plan: DailyPlan) -> str:
        """Generate a plain-English explanation of what was scheduled and why."""
        parts = [
            f"Scheduled {len(plan.scheduled_tasks)} task(s) using "
            f"{plan.total_minutes} of {self.owner.available_minutes} available minutes."
        ]
        if plan.skipped_tasks:
            skipped_names = ", ".join(t.name for t in plan.skipped_tasks)
            parts.append(f"Skipped due to time: {skipped_names}.")
        parts.append("Tasks were ordered by priority, with required tasks given preference.")
        return " ".join(parts)

    def detect_conflicts(self, tasks: list[Task]) -> list[str]:
        """Return warning messages for tasks that share the same 'HH:MM' time slot.

        Lightweight strategy: build a dict keyed by time, then flag any slot
        with more than one task. Tasks without a time value are ignored.
        Safe to call with tasks from multiple pets — pass a merged list.

        Args:
            tasks: the task list to check; may span one or more pets.

        Returns:
            A list of warning strings, one per conflicting slot.
            Empty list means no conflicts were found.
        """
        warnings = []
        seen: dict[str, list[Task]] = {}
        for task in tasks:
            if task.time is None:
                continue
            seen.setdefault(task.time, []).append(task)
        for time_slot, conflicting in seen.items():
            if len(conflicting) > 1:
                names = ", ".join(t.name for t in conflicting)
                warnings.append(f"WARNING: conflict at {time_slot} — {names}")
        return warnings

    def complete_task(self, task: Task) -> Task | None:
        """Mark a task complete and schedule its next occurrence if it recurs.

        Calls task.mark_complete(), then checks the recurrence field.
        If recurrence is 'daily' or 'weekly', a fresh copy of the task
        (completed=False) is created and appended to the pet's task list.
        Non-recurring tasks are marked done with no further action.

        Args:
            task: the task to complete; must belong to self.pet.

        Returns:
            The newly created next-occurrence Task, or None if non-recurring.
        """
        task.mark_complete()
        if task.recurrence not in ("daily", "weekly"):
            return None
        next_task = Task(
            name=task.name,
            duration_minutes=task.duration_minutes,
            priority=task.priority,
            preferred_time=task.preferred_time,
            time=task.time,
            is_required=task.is_required,
            recurrence=task.recurrence,
        )
        self.pet.add_task(next_task)
        return next_task

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Return tasks sorted chronologically by their 'HH:MM' time attribute.

        Uses a lambda key that returns a tuple: (time is None, time or "").
        The boolean first element pushes tasks without a time to the end.
        String comparison on 'HH:MM' is safe because lexicographic order
        matches chronological order for zero-padded hour strings.

        Args:
            tasks: the task list to sort; original list is not modified.

        Returns:
            A new list sorted earliest-to-latest, with untimed tasks last.
        """
        return sorted(tasks, key=lambda t: (t.time is None, t.time or ""))

    def filter_tasks(
        self,
        tasks: list[Task],
        *,
        completed: bool | None = None,
        pet_name: str | None = None,
    ) -> list[Task]:
        """Return a filtered subset of tasks based on completion status or pet name.

        Filters are keyword-only and independent — pass one or both.
        Passing None for a filter skips it entirely, so all values pass through.
        The pet_name filter checks against self.pet.name, so it is most useful
        when confirming that a task list belongs to the expected pet.

        Args:
            tasks:     the task list to filter; original list is not modified.
            completed: True keeps only finished tasks, False keeps only pending.
                       None disables this filter.
            pet_name:  keeps tasks only if self.pet.name matches this value.
                       None disables this filter.

        Returns:
            A new list containing only tasks that passed all active filters.
        """
        result = tasks
        if completed is not None:
            result = [t for t in result if t.completed == completed]
        if pet_name is not None:
            result = [t for t in result if self.pet.name == pet_name]
        return result

    def _sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks by priority level, promoting required tasks within ties."""
        return sorted(tasks, key=lambda t: (t.priority, not t.is_required))

    def _filter_by_time(self, tasks: list[Task]) -> list[Task]:
        """Reorder tasks so owner-preferred time-of-day tasks appear first."""
        preferences = self.owner.get_constraints().get("preferences", [])
        if not preferences:
            return tasks
        preferred = [t for t in tasks if t.preferred_time in preferences]
        others = [t for t in tasks if t.preferred_time not in preferences]
        return preferred + others
