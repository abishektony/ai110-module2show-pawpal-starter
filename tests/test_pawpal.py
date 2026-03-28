import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pawpal_system import Task, Pet, Owner
from scheduler import Scheduler


def make_scheduler(available_minutes=120, preferences=None, tasks=None):
    """Helper: build a Scheduler with one pet pre-loaded with tasks."""
    owner = Owner(name="Alex", available_minutes=available_minutes, preferences=preferences or [])
    pet = Pet(name="Buddy", species="Dog")
    for task in (tasks or []):
        pet.add_task(task)
    return Scheduler(owner=owner, pet=pet)


def test_mark_complete_changes_status():
    task = Task(name="Morning Walk", duration_minutes=30, priority=1)
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Buddy", species="Dog")
    assert len(pet.tasks) == 0
    pet.add_task(Task(name="Feeding", duration_minutes=10, priority=1))
    assert len(pet.tasks) == 1
    pet.add_task(Task(name="Grooming", duration_minutes=15, priority=2))
    assert len(pet.tasks) == 2


# --- Recurring Tasks ---

def test_complete_daily_task_adds_new_occurrence():
    task = Task(name="Feeding", duration_minutes=10, priority=1, recurrence="daily")
    scheduler = make_scheduler(tasks=[task])
    next_task = scheduler.complete_task(task)
    assert next_task is not None
    assert next_task.completed is False
    assert next_task.name == "Feeding"
    assert next_task.recurrence == "daily"
    assert len(scheduler.pet.tasks) == 2


def test_complete_weekly_task_adds_new_occurrence():
    task = Task(name="Bath", duration_minutes=20, priority=2, recurrence="weekly")
    scheduler = make_scheduler(tasks=[task])
    next_task = scheduler.complete_task(task)
    assert next_task is not None
    assert next_task.completed is False
    assert next_task.recurrence == "weekly"


def test_complete_non_recurring_task_returns_none():
    task = Task(name="Vet Visit", duration_minutes=60, priority=1, recurrence=None)
    scheduler = make_scheduler(tasks=[task])
    result = scheduler.complete_task(task)
    assert result is None
    assert len(scheduler.pet.tasks) == 1  # no new task added


def test_complete_unknown_recurrence_returns_none():
    task = Task(name="Monthly Trim", duration_minutes=30, priority=3, recurrence="monthly")
    scheduler = make_scheduler(tasks=[task])
    result = scheduler.complete_task(task)
    assert result is None  # "monthly" is not a supported recurrence


def test_complete_task_marks_original_done():
    task = Task(name="Walk", duration_minutes=30, priority=1, recurrence="daily")
    scheduler = make_scheduler(tasks=[task])
    scheduler.complete_task(task)
    assert task.completed is True


# --- Sorting ---

def test_sort_by_time_chronological_order():
    scheduler = make_scheduler()
    t1 = Task(name="Lunch", duration_minutes=10, priority=1, time="12:00")
    t2 = Task(name="Morning Walk", duration_minutes=30, priority=1, time="08:00")
    t3 = Task(name="Dinner", duration_minutes=10, priority=1, time="18:30")
    result = scheduler.sort_by_time([t1, t2, t3])
    assert [t.name for t in result] == ["Morning Walk", "Lunch", "Dinner"]


def test_sort_by_time_pushes_untimed_tasks_to_end():
    scheduler = make_scheduler()
    timed = Task(name="Walk", duration_minutes=30, priority=1, time="09:00")
    untimed = Task(name="Play", duration_minutes=20, priority=1, time=None)
    result = scheduler.sort_by_time([untimed, timed])
    assert result[0].name == "Walk"
    assert result[1].name == "Play"


def test_sort_by_time_all_untimed_is_stable():
    scheduler = make_scheduler()
    tasks = [
        Task(name="A", duration_minutes=10, priority=1, time=None),
        Task(name="B", duration_minutes=10, priority=1, time=None),
    ]
    result = scheduler.sort_by_time(tasks)
    assert len(result) == 2  # no crash, returns both


def test_priority_sort_required_task_promoted_within_tie():
    scheduler = make_scheduler()
    optional = Task(name="Play", duration_minutes=20, priority=2, is_required=False)
    required = Task(name="Meds", duration_minutes=5, priority=2, is_required=True)
    result = scheduler._sort_by_priority([optional, required])
    assert result[0].name == "Meds"


def test_priority_sort_lower_number_comes_first():
    scheduler = make_scheduler()
    low = Task(name="Bath", duration_minutes=20, priority=3)
    high = Task(name="Feeding", duration_minutes=10, priority=1)
    result = scheduler._sort_by_priority([low, high])
    assert result[0].name == "Feeding"


# --- Conflict Detection ---

def test_detect_conflicts_same_time_slot():
    scheduler = make_scheduler()
    t1 = Task(name="Walk", duration_minutes=30, priority=1, time="08:00")
    t2 = Task(name="Feeding", duration_minutes=10, priority=1, time="08:00")
    warnings = scheduler.detect_conflicts([t1, t2])
    assert len(warnings) == 1
    assert "08:00" in warnings[0]
    assert "Walk" in warnings[0]
    assert "Feeding" in warnings[0]


def test_detect_conflicts_no_conflict():
    scheduler = make_scheduler()
    t1 = Task(name="Walk", duration_minutes=30, priority=1, time="08:00")
    t2 = Task(name="Feeding", duration_minutes=10, priority=1, time="09:00")
    warnings = scheduler.detect_conflicts([t1, t2])
    assert warnings == []


def test_detect_conflicts_ignores_untimed_tasks():
    scheduler = make_scheduler()
    t1 = Task(name="Walk", duration_minutes=30, priority=1, time=None)
    t2 = Task(name="Play", duration_minutes=20, priority=1, time=None)
    warnings = scheduler.detect_conflicts([t1, t2])
    assert warnings == []


def test_detect_conflicts_three_tasks_same_slot():
    scheduler = make_scheduler()
    tasks = [
        Task(name="A", duration_minutes=10, priority=1, time="10:00"),
        Task(name="B", duration_minutes=10, priority=1, time="10:00"),
        Task(name="C", duration_minutes=10, priority=1, time="10:00"),
    ]
    warnings = scheduler.detect_conflicts(tasks)
    assert len(warnings) == 1  # one warning for the slot, not three pairs
    assert "A" in warnings[0] and "B" in warnings[0] and "C" in warnings[0]


# --- Schedule Building ---

def test_schedule_fits_tasks_within_available_time():
    tasks = [
        Task(name="Walk", duration_minutes=30, priority=1),
        Task(name="Feeding", duration_minutes=10, priority=2),
    ]
    scheduler = make_scheduler(available_minutes=40, tasks=tasks)
    plan = scheduler.schedule()
    assert len(plan.scheduled_tasks) == 2
    assert plan.total_minutes == 40


def test_schedule_skips_task_that_doesnt_fit():
    tasks = [
        Task(name="Walk", duration_minutes=30, priority=1),
        Task(name="Bath", duration_minutes=60, priority=2),
    ]
    scheduler = make_scheduler(available_minutes=30, tasks=tasks)
    plan = scheduler.schedule()
    assert len(plan.scheduled_tasks) == 1
    assert plan.scheduled_tasks[0].name == "Walk"
    assert len(plan.skipped_tasks) == 1
    assert plan.skipped_tasks[0].name == "Bath"


def test_schedule_zero_available_minutes_skips_all():
    tasks = [Task(name="Walk", duration_minutes=30, priority=1)]
    scheduler = make_scheduler(available_minutes=0, tasks=tasks)
    plan = scheduler.schedule()
    assert plan.scheduled_tasks == []
    assert len(plan.skipped_tasks) == 1


def test_schedule_no_tasks_returns_empty_plan():
    scheduler = make_scheduler(available_minutes=60, tasks=[])
    plan = scheduler.schedule()
    assert plan.scheduled_tasks == []
    assert plan.skipped_tasks == []
    assert plan.total_minutes == 0


def test_schedule_prefers_owner_preferences():
    tasks = [
        Task(name="Evening Walk", duration_minutes=30, priority=2, preferred_time="evening"),
        Task(name="Morning Feeding", duration_minutes=10, priority=2, preferred_time="morning"),
    ]
    scheduler = make_scheduler(available_minutes=40, preferences=["morning"], tasks=tasks)
    plan = scheduler.schedule()
    # Morning Feeding should be scheduled first due to owner preference
    assert plan.scheduled_tasks[0].name == "Morning Feeding"


# --- fits_in_time ---

def test_fits_in_time_true_when_within_limit():
    tasks = [Task(name="Walk", duration_minutes=20, priority=1)]
    scheduler = make_scheduler(available_minutes=30, tasks=tasks)
    assert scheduler.fits_in_time(tasks) is True


def test_fits_in_time_false_when_exceeds_limit():
    tasks = [Task(name="Bath", duration_minutes=60, priority=1)]
    scheduler = make_scheduler(available_minutes=30, tasks=tasks)
    assert scheduler.fits_in_time(tasks) is False


# --- filter_tasks ---

def test_filter_tasks_by_completed_false():
    tasks = [
        Task(name="Done", duration_minutes=10, priority=1, completed=True),
        Task(name="Pending", duration_minutes=10, priority=1, completed=False),
    ]
    scheduler = make_scheduler(tasks=tasks)
    result = scheduler.filter_tasks(tasks, completed=False)
    assert len(result) == 1
    assert result[0].name == "Pending"


def test_filter_tasks_by_pet_name_match():
    tasks = [Task(name="Walk", duration_minutes=30, priority=1)]
    scheduler = make_scheduler(tasks=tasks)
    result = scheduler.filter_tasks(tasks, pet_name="Buddy")
    assert len(result) == 1


def test_filter_tasks_by_pet_name_no_match():
    tasks = [Task(name="Walk", duration_minutes=30, priority=1)]
    scheduler = make_scheduler(tasks=tasks)
    result = scheduler.filter_tasks(tasks, pet_name="Mittens")
    assert result == []
