from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Task:
    name: str
    duration_minutes: int
    priority: int  # 1 = highest
    preferred_time: Optional[str] = None  # e.g. "morning", "evening"
    is_required: bool = False
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def __repr__(self) -> str:
        """Return a readable summary of the task."""
        required_tag = " [required]" if self.is_required else ""
        time_tag = f" ({self.preferred_time})" if self.preferred_time else ""
        return f"{self.name}{time_tag} — {self.duration_minutes} min, priority {self.priority}{required_tag}"


@dataclass
class Pet:
    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task_name: str) -> None:
        """Remove a task by name from this pet's task list."""
        self.tasks = [t for t in self.tasks if t.name != task_name]

    def get_tasks_by_priority(self) -> list[Task]:
        """Return tasks sorted by priority, with required tasks first within ties."""
        return sorted(self.tasks, key=lambda t: (t.priority, not t.is_required))


@dataclass
class Owner:
    name: str
    available_minutes: int
    preferences: list[str] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def get_constraints(self) -> dict:
        """Return the owner's scheduling constraints as a dictionary."""
        return {
            "available_minutes": self.available_minutes,
            "preferences": self.preferences,
        }


@dataclass
class DailyPlan:
    scheduled_tasks: list[Task] = field(default_factory=list)
    skipped_tasks: list[Task] = field(default_factory=list)
    total_minutes: int = 0
    reasoning: str = ""

    def display(self) -> str:
        """Format and return the full daily plan as a printable string."""
        lines = ["=== Daily Plan ==="]
        if self.scheduled_tasks:
            lines.append("\nScheduled:")
            for task in self.scheduled_tasks:
                lines.append(f"  - {task}")
            lines.append(f"\nTotal time: {self.total_minutes} min")
        else:
            lines.append("No tasks scheduled.")

        if self.skipped_tasks:
            lines.append("\nSkipped (not enough time):")
            for task in self.skipped_tasks:
                lines.append(f"  - {task}")

        lines.append(f"\nReasoning: {self.reasoning}")
        return "\n".join(lines)


@dataclass
class Scheduler:
    owner: Owner
    pet: Pet

    def schedule(self) -> DailyPlan:
        """Build and return a DailyPlan by fitting prioritized tasks into available time."""
        constraints = self.owner.get_constraints()
        available = constraints["available_minutes"]

        sorted_tasks = self._sort_by_priority(self.pet.tasks)
        filtered_tasks = self._filter_by_time(sorted_tasks)

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

    def _sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks by priority level, promoting required tasks within ties."""
        # Required tasks bubble up within same priority level
        return sorted(tasks, key=lambda t: (t.priority, not t.is_required))

    def _filter_by_time(self, tasks: list[Task]) -> list[Task]:
        """Reorder tasks so owner-preferred time-of-day tasks appear first."""
        preferences = self.owner.get_constraints().get("preferences", [])
        if not preferences:
            return tasks
        # Preferred-time tasks come first, others follow
        preferred = [t for t in tasks if t.preferred_time in preferences]
        others = [t for t in tasks if t.preferred_time not in preferences]
        return preferred + others
