from pawpal_system import Owner, Pet, Task
from scheduler import Scheduler


def main():
    # --- Create Owner ---
    owner = Owner(name="Alex", available_minutes=90, preferences=["morning"])

    # --- Create Pets ---
    buddy = Pet(name="Buddy", species="Dog")
    whiskers = Pet(name="Whiskers", species="Cat")

    # --- Add Tasks OUT OF ORDER (intentionally scrambled times) ---
    buddy.add_task(Task(name="Fetch / Playtime", duration_minutes=20, priority=2, preferred_time="afternoon", time="14:00"))
    buddy.add_task(Task(name="Grooming",         duration_minutes=15, priority=3, preferred_time="evening",   time="18:30"))
    buddy.add_task(Task(name="Feeding",          duration_minutes=10, priority=1, preferred_time="morning",   time="07:00", is_required=True))
    buddy.add_task(Task(name="Morning Walk",     duration_minutes=30, priority=1, preferred_time="morning",   time="08:00", is_required=True))

    whiskers.add_task(Task(name="Play Session",    duration_minutes=15, priority=3, preferred_time="evening",  time="19:00"))
    whiskers.add_task(Task(name="Litter Cleaning", duration_minutes=10, priority=2, preferred_time="morning",  time="09:00"))
    whiskers.add_task(Task(name="Feeding",         duration_minutes=10, priority=1, preferred_time="morning",  time="07:30", is_required=True))

    # --- Register Pets with Owner ---
    owner.add_pet(buddy)
    owner.add_pet(whiskers)

    # --- Schedule and Print ---
    print("=" * 40)
    print("        TODAY'S SCHEDULE — PawPal+")
    print("=" * 40)
    print(f"Owner : {owner.name}")
    print(f"Time  : {owner.available_minutes} minutes available\n")

    for pet in owner.pets:
        print(f"--- {pet.name} ({pet.species}) ---")
        scheduler = Scheduler(owner=owner, pet=pet)
        plan = scheduler.schedule()
        print(plan.display())
        print()

    # --- Test sort_by_time() ---
    print("=" * 40)
    print("  BUDDY'S TASKS — sorted by time")
    print("=" * 40)
    buddy_scheduler = Scheduler(owner=owner, pet=buddy)
    for task in buddy_scheduler.sort_by_time(buddy.tasks):
        print(f"  {task.time or 'no time':>5}  {task}")
    print()

    # --- Test filter_tasks(): incomplete tasks only ---
    print("=" * 40)
    print("  BUDDY'S TASKS — incomplete only")
    print("=" * 40)
    incomplete = buddy_scheduler.filter_tasks(buddy.tasks, completed=False)
    for task in incomplete:
        print(f"  {task}")
    print()

    # --- Mark one task complete, then filter again ---
    buddy.tasks[0].mark_complete()
    print("=" * 40)
    print(f"  Marked '{buddy.tasks[0].name}' complete.")
    print("  BUDDY'S TASKS — incomplete after mark")
    print("=" * 40)
    incomplete_after = buddy_scheduler.filter_tasks(buddy.tasks, completed=False)
    for task in incomplete_after:
        print(f"  {task}")
    print()

    # --- Test filter_tasks(): by pet name ---
    print("=" * 40)
    print("  filter_tasks(pet_name='Buddy') on Buddy's scheduler")
    print("=" * 40)
    matched = buddy_scheduler.filter_tasks(buddy.tasks, pet_name="Buddy")
    print(f"  Matched {len(matched)} task(s) (expected {len(buddy.tasks)})")
    no_match = buddy_scheduler.filter_tasks(buddy.tasks, pet_name="Whiskers")
    print(f"  Matched {len(no_match)} task(s) for 'Whiskers' (expected 0)")
    print()

    # --- Test detect_conflicts() ---
    print("=" * 40)
    print("  CONFLICT DETECTION TEST")
    print("=" * 40)

    luna = Pet(name="Luna", species="Cat")
    luna.add_task(Task(name="Feeding",      duration_minutes=10, priority=1, time="07:00", is_required=True))
    luna.add_task(Task(name="Medication",   duration_minutes=5,  priority=1, time="07:00", is_required=True))  # conflict
    luna.add_task(Task(name="Play Session", duration_minutes=15, priority=2, time="09:00"))
    luna.add_task(Task(name="Brushing",     duration_minutes=10, priority=3, time="09:00"))  # conflict
    luna.add_task(Task(name="Vet Check",    duration_minutes=30, priority=2, time="14:00"))  # no conflict

    luna_scheduler = Scheduler(owner=owner, pet=luna)
    conflicts = luna_scheduler.detect_conflicts(luna.tasks)

    if conflicts:
        for warning in conflicts:
            print(f"  {warning}")
    else:
        print("  No conflicts found.")
    print()

    # --- Cross-pet conflict check (all tasks in one list) ---
    print("=" * 40)
    print("  CROSS-PET CONFLICT CHECK (Buddy + Luna)")
    print("=" * 40)
    all_tasks = buddy.tasks + luna.tasks
    cross_conflicts = buddy_scheduler.detect_conflicts(all_tasks)
    if cross_conflicts:
        for warning in cross_conflicts:
            print(f"  {warning}")
    else:
        print("  No cross-pet conflicts found.")
    print()

    # --- Test complete_task() with recurrence ---
    print("=" * 40)
    print("  RECURRENCE TEST")
    print("=" * 40)

    rex = Pet(name="Rex", species="Dog")
    rex.add_task(Task(name="Morning Walk", duration_minutes=30, priority=1,
                      preferred_time="morning", time="07:00",
                      is_required=True, recurrence="daily"))
    rex.add_task(Task(name="Bath Time",    duration_minutes=20, priority=3,
                      preferred_time="evening", time="18:00",
                      recurrence="weekly"))
    rex.add_task(Task(name="Vet Visit",    duration_minutes=60, priority=2,
                      preferred_time="morning", time="10:00"))  # no recurrence

    rex_scheduler = Scheduler(owner=owner, pet=rex)

    print(f"  Tasks before completing any: {len(rex.tasks)}")
    for t in rex.tasks:
        print(f"    {t}  [recurrence={t.recurrence}]")
    print()

    for task in list(rex.tasks):  # copy so iteration isn't affected by additions
        next_t = rex_scheduler.complete_task(task)
        if next_t:
            print(f"  Completed '{task.name}' ({task.recurrence}) -> next occurrence added")
        else:
            print(f"  Completed '{task.name}' (no recurrence) -> nothing added")

    print(f"\n  Tasks after completing all: {len(rex.tasks)}")
    for t in rex.tasks:
        status = "done" if t.completed else "pending"
        print(f"    [{status}] {t}  [recurrence={t.recurrence}]")


if __name__ == "__main__":
    main()
