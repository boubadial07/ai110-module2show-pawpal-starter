"""PawPal+ core system.

Implements the classes described in diagrams/uml.mmd: the Owner -> Pet -> Task
data model plus a Scheduler that turns a set of tasks into a daily plan based on
priority and an available-time budget.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


# Allowed priority values, ordered from most to least important.
PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


def _priority_rank(priority: str) -> int:
    """Sort key for a priority string; unknown values sort last."""
    return PRIORITY_ORDER.get(priority, len(PRIORITY_ORDER))


@dataclass
class Task:
    """A single pet care task (e.g. 'Morning walk')."""

    title: str
    duration_minutes: int
    priority: str = "medium"
    due_date: date | None = None
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def is_overdue(self, today: date | None = None) -> bool:
        """Return True if the task has a past due_date and isn't done yet.

        `today` is injectable so tests don't depend on the real clock.
        """
        if self.completed or self.due_date is None:
            return False
        today = today or date.today()
        return self.due_date < today


@dataclass
class Pet:
    """A pet that has care tasks."""

    name: str
    species: str
    age: int = 0
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a care task to this pet."""
        self.tasks.append(task)

    def complete_task(self, task: Task) -> None:
        """Mark one of this pet's tasks complete.

        Raises ValueError if the task doesn't belong to this pet.
        """
        if task not in self.tasks:
            raise ValueError(f"{task.title!r} is not a task for {self.name}")
        task.mark_complete()

    def view_tasks(self) -> list[Task]:
        """Return this pet's tasks."""
        return list(self.tasks)


@dataclass
class Owner:
    """A pet owner who can have one or more pets."""

    name: str
    email: str = ""
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner.

        Raises ValueError if the pet isn't owned.
        """
        if pet not in self.pets:
            raise ValueError(f"{pet.name!r} is not owned by {self.name}")
        self.pets.remove(pet)

    def view_pets(self) -> list[Pet]:
        """Return this owner's pets."""
        return list(self.pets)


@dataclass
class DailyPlan:
    """The result of scheduling: what got planned, what got skipped, and why."""

    scheduled: list[Task] = field(default_factory=list)
    skipped: list[Task] = field(default_factory=list)
    explanation: str = ""

    @property
    def total_minutes(self) -> int:
        """Total minutes of scheduled tasks."""
        return sum(t.duration_minutes for t in self.scheduled)


class Scheduler:
    """Turns a set of tasks into a daily plan based on constraints."""

    def __init__(self, tasks: list[Task] | None = None) -> None:
        self.tasks: list[Task] = tasks or []

    def sort_tasks(self) -> list[Task]:
        """Return tasks ordered by priority, then due date, then duration.

        Higher priority first; among equal priority, the soonest due date wins,
        and shorter tasks break any remaining ties. Does not mutate self.tasks.
        """
        return sorted(
            self.tasks,
            key=lambda t: (
                _priority_rank(t.priority),
                t.due_date or date.max,
                t.duration_minutes,
            ),
        )

    def detect_conflicts(self) -> list[tuple[Task, Task]]:
        """Return pairs of tasks that share the same (case-insensitive) title.

        With no start times in the model, the meaningful conflict is a
        duplicate task the owner added twice.
        """
        conflicts: list[tuple[Task, Task]] = []
        for i, a in enumerate(self.tasks):
            for b in self.tasks[i + 1:]:
                if a.title.strip().lower() == b.title.strip().lower():
                    conflicts.append((a, b))
        return conflicts

    def get_today_tasks(self, today: date | None = None) -> list[Task]:
        """Return incomplete tasks that are relevant today.

        A task is relevant if it has no due date (do-anytime) or is due on or
        before today (due or overdue). Returned in scheduling order.
        """
        today = today or date.today()
        relevant = [
            t
            for t in self.sort_tasks()
            if not t.completed and (t.due_date is None or t.due_date <= today)
        ]
        return relevant

    def build_plan(
        self, available_minutes: int, today: date | None = None
    ) -> DailyPlan:
        """Pack today's most important tasks into the time budget.

        Greedy by scheduling order: walk highest-priority-first and add each
        task that still fits, skipping the ones that don't. Returns a DailyPlan
        with the chosen tasks, the skipped ones, and a plain-language
        explanation of the choices.
        """
        if available_minutes < 0:
            raise ValueError("available_minutes cannot be negative")

        candidates = self.get_today_tasks(today)
        scheduled: list[Task] = []
        skipped: list[Task] = []
        remaining = available_minutes

        for task in candidates:
            if task.duration_minutes <= remaining:
                scheduled.append(task)
                remaining -= task.duration_minutes
            else:
                skipped.append(task)

        explanation = self._explain(
            available_minutes, scheduled, skipped, remaining
        )
        return DailyPlan(scheduled=scheduled, skipped=skipped, explanation=explanation)

    @staticmethod
    def _explain(
        budget: int,
        scheduled: list[Task],
        skipped: list[Task],
        remaining: int,
    ) -> str:
        """Build a human-readable explanation of a plan."""
        lines = [
            f"Planned {len(scheduled)} task(s) within a {budget}-minute budget "
            f"({budget - remaining} min used, {remaining} min free)."
        ]
        for task in scheduled:
            lines.append(
                f"  • {task.title} ({task.duration_minutes} min) "
                f"— chosen: {task.priority} priority."
            )
        for task in skipped:
            lines.append(
                f"  • Skipped {task.title} ({task.duration_minutes} min) "
                f"— {task.priority} priority, didn't fit remaining time."
            )
        return "\n".join(lines)
