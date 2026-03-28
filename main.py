from pawpal_system import Owner, Pet, Task, Scheduler


def main():
    # --- Create Owner ---
    owner = Owner(name="Alex", available_minutes=90, preferences=["morning"])

    # --- Create Pets ---
    buddy = Pet(name="Buddy", species="Dog")
    whiskers = Pet(name="Whiskers", species="Cat")

    # --- Add Tasks to Buddy (Dog) ---
    buddy.add_task(Task(name="Morning Walk",     duration_minutes=30, priority=1, preferred_time="morning",  is_required=True))
    buddy.add_task(Task(name="Feeding",          duration_minutes=10, priority=1, preferred_time="morning",  is_required=True))
    buddy.add_task(Task(name="Fetch / Playtime", duration_minutes=20, priority=2, preferred_time="afternoon"))
    buddy.add_task(Task(name="Grooming",         duration_minutes=15, priority=3, preferred_time="evening"))

    # --- Add Tasks to Whiskers (Cat) ---
    whiskers.add_task(Task(name="Feeding",        duration_minutes=10, priority=1, preferred_time="morning",  is_required=True))
    whiskers.add_task(Task(name="Litter Cleaning",duration_minutes=10, priority=2, preferred_time="morning"))
    whiskers.add_task(Task(name="Play Session",   duration_minutes=15, priority=3, preferred_time="evening"))

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


if __name__ == "__main__":
    main()
