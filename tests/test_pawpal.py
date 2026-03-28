import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pawpal_system import Task, Pet


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
