from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Task:
    name: str
    duration_minutes: int
    priority: int  # 1 = highest
    preferred_time: Optional[str] = None  # e.g. "morning", "evening"
    is_required: bool = False

    def __repr__(self) -> str:
        pass


@dataclass
class Pet:
    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, task_name: str) -> None:
        pass

    def get_tasks_by_priority(self) -> list[Task]:
        pass


@dataclass
class Owner:
    name: str
    available_minutes: int
    preferences: list[str] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        pass

    def get_constraints(self) -> dict:
        pass


@dataclass
class DailyPlan:
    scheduled_tasks: list[Task] = field(default_factory=list)
    skipped_tasks: list[Task] = field(default_factory=list)
    total_minutes: int = 0
    reasoning: str = ""

    def display(self) -> str:
        pass


@dataclass
class Scheduler:
    owner: Owner
    pet: Pet

    def schedule(self) -> DailyPlan:
        pass

    def fits_in_time(self, tasks: list[Task]) -> bool:
        pass

    def explain_plan(self, plan: DailyPlan) -> str:
        pass

    def _sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        pass

    def _filter_by_time(self, tasks: list[Task]) -> list[Task]:
        pass
