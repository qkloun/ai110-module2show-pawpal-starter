# Testing scriipt for the system.
from pawpal_system import Owner, Pet, Scheduler, Task


def main() -> None:
    owner = Owner(name="Yunus", available_minutes=75, day_start="07:30")

    mochi = Pet(name="Loki", species="dog")
    luna = Pet(name="Luna", species="cat")
    owner.add_pet(mochi)
    owner.add_pet(luna)

    mochi.add_task(Task("Morning walk", 30, "high", time="07:30"))
    mochi.add_task(Task("Heartworm pill", 5, "high", time="08:00"))
    mochi.add_task(Task("Brush coat", 15, "low", time="18:00", frequency="weekly"))
    luna.add_task(Task("Breakfast", 10, "high", time="07:45"))
    luna.add_task(Task("Play session", 20, "medium", time="17:00"))
    luna.add_task(Task("Clean litter box", 10, "medium", time="09:00"))

    scheduler = Scheduler(owner)
    plan = scheduler.build_daily_plan()

    print("=" * 60)
    print(f"  Today's Schedule for {owner.name}'s pets")
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