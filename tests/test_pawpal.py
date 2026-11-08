"""Basic tests for the PawPal+ logic layer."""

from pawpal_system import Pet, Task


def test_mark_complete_changes_status():
    task = Task("Morning walk", 30, "high")
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet("Mochi", "dog")
    assert len(pet.tasks) == 0

    pet.add_task(Task("Breakfast", 10, "high"))

    assert len(pet.tasks) == 1


# --- Recurring tasks ---

from datetime import date, timedelta  # noqa: E402

from pawpal_system import Owner, Scheduler  # noqa: E402

TODAY = date(2026, 11, 8)


def make_scheduler(task):
    """Build an owner with one pet holding the given task."""
    owner = Owner("Jordan", 60)
    pet = Pet("Mochi", "dog")
    owner.add_pet(pet)
    pet.add_task(task)
    return Scheduler(owner, today=TODAY), pet


def test_completing_daily_task_creates_next_day_copy():
    scheduler, pet = make_scheduler(Task("Walk", 30, "high", due_date=TODAY))

    next_task = scheduler.complete_task("Mochi", "Walk")

    assert pet.tasks[0].completed is True
    assert next_task.due_date == TODAY + timedelta(days=1)
    assert next_task.completed is False
    assert len(pet.tasks) == 2


def test_completing_weekly_task_creates_copy_one_week_later():
    scheduler, _ = make_scheduler(
        Task("Brush", 15, "low", frequency="weekly", due_date=TODAY))

    next_task = scheduler.complete_task("Mochi", "Brush")

    assert next_task.due_date == TODAY + timedelta(days=7)


def test_completing_one_time_task_creates_nothing():
    scheduler, pet = make_scheduler(
        Task("Vet visit", 60, "high", frequency="once", due_date=TODAY))

    assert scheduler.complete_task("Mochi", "Vet visit") is None
    assert len(pet.tasks) == 1


def test_tomorrows_copy_is_not_in_todays_plan():
    scheduler, _ = make_scheduler(Task("Walk", 30, "high", due_date=TODAY))
    scheduler.complete_task("Mochi", "Walk")

    assert scheduler.build_daily_plan() == []


# --- Conflict detection ---

def test_same_time_tasks_for_different_pets_are_flagged():
    owner = Owner("Jordan", 60)
    mochi, luna = Pet("Mochi", "dog"), Pet("Luna", "cat")
    owner.add_pet(mochi)
    owner.add_pet(luna)
    mochi.add_task(Task("Walk", 30, "high", time="08:00", due_date=TODAY))
    luna.add_task(Task("Feeding", 10, "high", time="08:00", due_date=TODAY))

    warnings = Scheduler(owner, today=TODAY).detect_conflicts()

    assert len(warnings) == 1
    assert "different pets" in warnings[0]


def test_back_to_back_tasks_are_not_a_conflict():
    scheduler, pet = make_scheduler(Task("Walk", 30, "high", time="08:00", due_date=TODAY))
    pet.add_task(Task("Pill", 5, "high", time="08:30", due_date=TODAY))

    assert scheduler.detect_conflicts() == []


def test_completed_tasks_do_not_cause_conflicts():
    scheduler, pet = make_scheduler(Task("Walk", 30, "high", time="08:00", due_date=TODAY))
    pet.add_task(Task("Pill", 5, "high", time="08:10", frequency="once", due_date=TODAY))
    scheduler.complete_task("Mochi", "Pill")

    assert scheduler.detect_conflicts() == []