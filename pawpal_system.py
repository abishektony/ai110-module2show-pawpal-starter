from __future__ import annotations
import json
from dataclasses import dataclass, field
from typing import Optional


PRIORITY_LABELS = {1: "🔴 High", 2: "🟡 Medium", 3: "🟢 Low"}
PRIORITY_MAP = {"High": 1, "Medium": 2, "Low": 3}


@dataclass
class Task:
    name: str
    duration_minutes: int
    priority: int  # 1 = High, 2 = Medium, 3 = Low
    preferred_time: Optional[str] = None  # e.g. "morning", "evening"
    time: Optional[str] = None  # e.g. "08:30" — used for chronological ordering
    is_required: bool = False
    completed: bool = False
    recurrence: Optional[str] = None  # "daily", "weekly", or None

    @property
    def priority_label(self) -> str:
        """Return a human-readable, emoji-coded priority label."""
        return PRIORITY_LABELS.get(self.priority, f"P{self.priority}")

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def __repr__(self) -> str:
        """Return a readable summary of the task."""
        required_tag = " [required]" if self.is_required else ""
        time_tag = f" ({self.preferred_time})" if self.preferred_time else ""
        return f"{self.name}{time_tag} — {self.duration_minutes} min, {self.priority_label}{required_tag}"


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

    def save_to_json(self, path: str = "data.json") -> None:
        """Persist the owner, their pets, and all tasks to a JSON file."""
        data = {
            "name": self.name,
            "available_minutes": self.available_minutes,
            "preferences": self.preferences,
            "pets": [
                {
                    "name": pet.name,
                    "species": pet.species,
                    "tasks": [
                        {
                            "name": t.name,
                            "duration_minutes": t.duration_minutes,
                            "priority": t.priority,
                            "preferred_time": t.preferred_time,
                            "time": t.time,
                            "is_required": t.is_required,
                            "completed": t.completed,
                            "recurrence": t.recurrence,
                        }
                        for t in pet.tasks
                    ],
                }
                for pet in self.pets
            ],
        }
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load_from_json(cls, path: str = "data.json") -> Owner:
        """Load an Owner (with pets and tasks) from a JSON file."""
        with open(path) as f:
            data = json.load(f)
        owner = cls(
            name=data["name"],
            available_minutes=data["available_minutes"],
            preferences=data.get("preferences", []),
        )
        for pet_data in data.get("pets", []):
            pet = Pet(name=pet_data["name"], species=pet_data["species"])
            for t in pet_data.get("tasks", []):
                pet.add_task(Task(
                    name=t["name"],
                    duration_minutes=t["duration_minutes"],
                    priority=t["priority"],
                    preferred_time=t.get("preferred_time"),
                    time=t.get("time"),
                    is_required=t.get("is_required", False),
                    completed=t.get("completed", False),
                    recurrence=t.get("recurrence"),
                ))
            owner.add_pet(pet)
        return owner


@dataclass
class DailyPlan:
    scheduled_tasks: list[Task] = field(default_factory=list)
    skipped_tasks: list[Task] = field(default_factory=list)
    total_minutes: int = 0
    reasoning: str = ""

    def display(self) -> str:
        """Format and return the full daily plan as a printable string."""
        from tabulate import tabulate

        lines = []
        if self.scheduled_tasks:
            rows = [
                [
                    t.priority_label,
                    t.name,
                    t.time or "—",
                    f"{t.duration_minutes} min",
                    "✓" if t.is_required else "",
                    t.recurrence or "—",
                ]
                for t in self.scheduled_tasks
            ]
            lines.append(tabulate(
                rows,
                headers=["Priority", "Task", "Time", "Duration", "Required", "Recurrence"],
                tablefmt="rounded_outline",
            ))
            lines.append(f"\n  Total: {self.total_minutes} min scheduled")
        else:
            lines.append("  No tasks scheduled.")

        if self.skipped_tasks:
            skipped_rows = [
                [t.priority_label, t.name, f"{t.duration_minutes} min"]
                for t in self.skipped_tasks
            ]
            lines.append("\n  Skipped (not enough time):")
            lines.append(tabulate(skipped_rows, headers=["Priority", "Task", "Duration"], tablefmt="simple"))

        lines.append(f"\n  Reasoning: {self.reasoning}")
        return "\n".join(lines)

