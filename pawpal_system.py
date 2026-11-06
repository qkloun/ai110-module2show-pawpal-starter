"""PawPal+ logic layer: backend classes for pets, tasks, and scheduling.

Skeleton generated from diagrams/uml_draft.mmd. Methods are stubs for now.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Task:
    """A single pet care task, such as a walk or a feeding."""

    title: str
    duration_minutes: int
    priority: str = "medium"  # "low", "medium", or "high"
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as done."""
        pass

    def priority_score(self) -> int:
        """Return a number for sorting (higher means more important)."""
        pass


@dataclass
class Pet:
    """A pet and the care tasks that belong to it."""

    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task for this pet."""
        pass

    def get_pending_tasks(self) -> list[Task]:
        """Return the tasks that are not completed yet."""
        pass


@dataclass
class Owner:
    """A pet owner, their pets, and how much time they have today."""

    name: str
    available_minutes: int
    day_start: str = "08:00"  # "HH:MM", 24-hour clock
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        pass

    def get_pet(self, name: str) -> Pet | None:
        """Find a pet by name, or return None if there isn't one."""
        pass

    def get_all_tasks(self) -> list[Task]:
        """Collect tasks from every pet into one list."""
        pass


class Scheduler:
    """Builds and explains a daily care plan for an owner's pets."""

    def __init__(self, owner: Owner) -> None:
        self.owner = owner
        # Each entry: (start_time "HH:MM", task, reason)
        self.plan: list[tuple[str, Task, str]] = []

    def sort_tasks(self, tasks: list[Task]) -> list[Task]:
        """Return tasks ordered by priority (most important first)."""
        pass

    def build_daily_plan(self) -> list[tuple[str, Task, str]]:
        """Fit tasks into the owner's available time and store the plan."""
        pass

    def explain_plan(self) -> str:
        """Return a readable explanation of the plan and why it looks that way."""
        pass