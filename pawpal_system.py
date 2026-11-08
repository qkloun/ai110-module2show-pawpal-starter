from __future__ import annotations

from dataclasses import dataclass, field

PRIORITY_SCORES = {"low": 1, "medium": 2, "high": 3}
FREQUENCIES = ("daily", "weekly", "once")


def to_minutes(hhmm: str) -> int:
    """Convert "HH:MM" to minutes after midnight."""
    hours, minutes = hhmm.split(":")
    hours, minutes = int(hours), int(minutes)
    if not (0 <= hours < 24 and 0 <= minutes < 60):
        raise ValueError(f"Invalid time: {hhmm!r}")
    return hours * 60 + minutes


def to_hhmm(total_minutes: int) -> str:
    """Convert minutes after midnight to "HH:MM"."""
    return f"{total_minutes // 60:02d}:{total_minutes % 60:02d}"


@dataclass
class Task:
    """A single pet care task, such as a walk or a feeding."""

    title: str
    duration_minutes: int
    priority: str = "medium"       # "low", "medium", or "high"
    time: str | None = None        # preferred start time "HH:MM", optional
    frequency: str = "daily"       # "daily", "weekly", or "once"
    completed: bool = False

    def __post_init__(self) -> None:
        """Normalize priority and reject invalid task values."""
        self.priority = self.priority.lower()
        if self.priority not in PRIORITY_SCORES:
            raise ValueError(f"Priority must be one of {list(PRIORITY_SCORES)}")
        if self.duration_minutes <= 0:
            raise ValueError("Duration must be a positive number of minutes")
        if self.frequency not in FREQUENCIES:
            raise ValueError(f"Frequency must be one of {list(FREQUENCIES)}")
        if self.time is not None:
            # Validate, then store zero-padded ("8:00" -> "08:00") so times sort as strings
            self.time = to_hhmm(to_minutes(self.time))

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def priority_score(self) -> int:
        """Return a number for sorting (higher means more important)."""
        return PRIORITY_SCORES[self.priority]


@dataclass
class Pet:
    """A pet and the care tasks that belong to it."""

    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task for this pet."""
        self.tasks.append(task)

    def remove_task(self, title: str) -> bool:
        """Remove the first task with this title. Return True if one was removed."""
        for task in self.tasks:
            if task.title == title:
                self.tasks.remove(task)
                return True
        return False

    def get_pending_tasks(self) -> list[Task]:
        """Return the tasks that are not completed yet."""
        return [task for task in self.tasks if not task.completed]


@dataclass
class Owner:
    """A pet owner, their pets, and how much time they have today."""

    name: str
    available_minutes: int
    day_start: str = "08:00"  # "HH:MM", 24-hour clock
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner. Pet names must be unique."""
        if self.get_pet(pet.name) is not None:
            raise ValueError(f"{self.name} already has a pet named {pet.name}")
        self.pets.append(pet)

    def get_pet(self, name: str) -> Pet | None:
        """Find a pet by name (case-insensitive), or return None."""
        for pet in self.pets:
            if pet.name.lower() == name.lower():
                return pet
        return None

    def get_all_tasks(self) -> list[tuple[Pet, Task]]:
        """Collect every pet's tasks into one list of (pet, task) pairs."""
        return [(pet, task) for pet in self.pets for task in pet.tasks]


@dataclass
class ScheduledTask:
    """One entry in the daily plan: when a task happens and why."""

    start_time: str
    pet: Pet
    task: Task
    reason: str

    @property
    def end_time(self) -> str:
        """Return the "HH:MM" time this task finishes."""
        return to_hhmm(to_minutes(self.start_time) + self.task.duration_minutes)


class Scheduler:
    """Builds and explains a daily care plan for an owner's pets."""

    def __init__(self, owner: Owner) -> None:
        """Set up a scheduler for one owner with an empty plan."""
        self.owner = owner
        self.plan: list[ScheduledTask] = []
        self.skipped: list[tuple[Pet, Task, str]] = []

    def get_pending_tasks(self) -> list[tuple[Pet, Task]]:
        """Ask the owner for all tasks, keeping only the unfinished ones."""
        return [(pet, task) for pet, task in self.owner.get_all_tasks()
                if not task.completed]

    def sort_tasks(self, pairs: list[tuple[Pet, Task]]) -> list[tuple[Pet, Task]]:
        """Order by priority (high first), then preferred time, then shorter duration."""
        def key(pair: tuple[Pet, Task]) -> tuple[int, int, int]:
            """Build the sort key for one (pet, task) pair."""
            _, task = pair
            preferred = to_minutes(task.time) if task.time else 24 * 60
            return (-task.priority_score(), preferred, task.duration_minutes)
        return sorted(pairs, key=key)

    def sort_by_time(self, pairs: list[tuple[Pet, Task]] | None = None
                     ) -> list[tuple[Pet, Task]]:
        """Return (pet, task) pairs ordered by preferred time, untimed tasks last."""
        if pairs is None:
            pairs = self.owner.get_all_tasks()
        return sorted(pairs, key=lambda pair: (pair[1].time is None, pair[1].time or ""))

    def filter_tasks(self, pet_name: str | None = None, completed: bool | None = None
                     ) -> list[tuple[Pet, Task]]:
        """Return (pet, task) pairs matching a pet name and/or completion status."""
        results = []
        for pet, task in self.owner.get_all_tasks():
            if pet_name is not None and pet.name.lower() != pet_name.lower():
                continue
            if completed is not None and task.completed != completed:
                continue
            results.append((pet, task))
        return results

    def build_daily_plan(self) -> list[ScheduledTask]:
        """Fit tasks into the owner's available time, most important first."""
        self.plan, self.skipped = [], []
        remaining = self.owner.available_minutes
        clock = to_minutes(self.owner.day_start)

        for pet, task in self.sort_tasks(self.get_pending_tasks()):
            if task.duration_minutes > remaining:
                self.skipped.append((
                    pet, task,
                    f"needs {task.duration_minutes} min but only {remaining} min left",
                ))
                continue
            reason = f"{task.priority} priority"
            if task.time:
                reason += f", preferred around {task.time}"
            self.plan.append(ScheduledTask(to_hhmm(clock), pet, task, reason))
            clock += task.duration_minutes
            remaining -= task.duration_minutes

        return self.plan

    def complete_task(self, pet_name: str, title: str) -> bool:
        """Mark a pet's task complete. Return True if it was found."""
        pet = self.owner.get_pet(pet_name)
        if pet is None:
            return False
        for task in pet.tasks:
            if task.title == title and not task.completed:
                task.mark_complete()
                return True
        return False

    def explain_plan(self) -> str:
        """Return a readable explanation of the plan and why it looks that way."""
        if not self.plan and not self.skipped:
            return "No pending tasks to schedule."

        used = sum(entry.task.duration_minutes for entry in self.plan)
        lines = [f"Daily plan for {self.owner.name} "
                 f"({used} of {self.owner.available_minutes} min used):"]
        for entry in self.plan:
            lines.append(
                f"  {entry.start_time}-{entry.end_time}  {entry.pet.name}: "
                f"{entry.task.title} ({entry.task.duration_minutes} min) - {entry.reason}"
            )
        if self.skipped:
            lines.append("Skipped:")
            for pet, task, reason in self.skipped:
                lines.append(f"  {pet.name}: {task.title} - {reason}")
        return "\n".join(lines)