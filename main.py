from pawpal_system import Owner, Pet, Scheduler, Task


def possessive(name: str) -> str:
    """Return "James'" or "Jordan's" depending on the last letter."""
    return f"{name}'" if name.lower().endswith("s") else f"{name}'s"


def print_tasks(heading: str, pairs) -> None:
    """Print a list of (pet, task) pairs as a small table."""
    print(f"\n{heading}")
    if not pairs:
        print("  (none)")
    for pet, task in pairs:
        status = "done" if task.completed else "todo"
        print(f"  {task.due_date:%a %b %d}  {task.time or '--:--'}  {pet.name:<6} "
              f"{task.title:<18} [{task.priority}, {task.frequency}] ({status})")


def main() -> None:
    owner = Owner(name="Jordan", available_minutes=75, day_start="07:30")

    mochi = Pet(name="Mochi", species="dog")
    luna = Pet(name="Luna", species="cat")
    owner.add_pet(mochi)
    owner.add_pet(luna)

    # Added deliberately out of time order
    luna.add_task(Task("Play session", 20, "medium", time="17:00"))
    mochi.add_task(Task("Brush coat", 15, "low", time="18:00", frequency="weekly"))
    mochi.add_task(Task("Heartworm pill", 5, "high", time="8:00"))   # not zero-padded
    luna.add_task(Task("Clean litter box", 10, "medium", time="09:00"))
    mochi.add_task(Task("Morning walk", 30, "high", time="07:30"))
    luna.add_task(Task("Breakfast", 10, "high", time="07:45"))
    luna.add_task(Task("Trim claws", 10, "low", frequency="once"))   # no time, one-off

    scheduler = Scheduler(owner)
    scheduler.complete_task("Luna", "Breakfast")

    print("=" * 60)
    print("  Sorting and filtering checks")
    print("=" * 60)
    print_tasks("All tasks, unsorted (grouped by pet, in the order added):", owner.get_all_tasks())
    print_tasks("Sorted by time:", scheduler.sort_by_time())
    print_tasks("Only Luna's tasks:", scheduler.filter_tasks(pet_name="Luna"))
    print_tasks("Only completed tasks:", scheduler.filter_tasks(completed=True))
    print_tasks("Mochi's pending tasks, sorted by time:",
                scheduler.sort_by_time(scheduler.filter_tasks(pet_name="Mochi",
                                                              completed=False)))

    print("\n" + "=" * 60)
    print("  Recurring task checks")
    print("=" * 60)
    for pet_name, title in [("Mochi", "Morning walk"), ("Mochi", "Brush coat"),
                            ("Luna", "Trim claws")]:
        next_task = scheduler.complete_task(pet_name, title)
        if next_task:
            print(f"  Completed {pet_name}'s {title} ({next_task.frequency}) "
                  f"-> next one due {next_task.due_date:%a %b %d}")
        else:
            print(f"  Completed {pet_name}'s {title} -> no repeat")
    print_tasks("Mochi's tasks after completing:",
                scheduler.sort_by_time(scheduler.filter_tasks(pet_name="Mochi")))

    plan = scheduler.build_daily_plan()
    print("\n" + "=" * 60)
    print(f"  Today's Schedule for {possessive(owner.name)} pets")
    print("=" * 60)
    for entry in plan:
        print(f"  {entry.start_time} - {entry.end_time}   "
              f"{entry.pet.name:<6} {entry.task.title:<18} [{entry.task.priority}]")
    print("-" * 60)
    used = sum(entry.task.duration_minutes for entry in plan)
    print(f"  Time used: {used} of {owner.available_minutes} minutes")
    if scheduler.skipped:
        print("\n  Not scheduled today:")
        for pet, task, reason in scheduler.skipped:
            print(f"    - {pet.name}: {task.title} ({reason})")
    print("=" * 60)


if __name__ == "__main__":
    main()