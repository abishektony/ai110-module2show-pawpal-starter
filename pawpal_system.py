from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Task:
    name: str
    duration_minutes: int
    priority: int  # 1 = highest
    preferred_time: Optional[str] = None  # e.g. "morning", "evening"
    time: Optional[str] = None  # e.g. "08:30" — used for chronological ordering
    is_required: bool = False
    completed: bool = False
    recurrence: Optional[str] = None  # "daily", "weekly", or None

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

