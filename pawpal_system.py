from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Optional

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}
DAY_START = "08:00"
RECURRENCE_INTERVALS = {"daily": timedelta(days=1), "weekly": timedelta(days=7)}


@dataclass
class Pet:
    name: str
    species: str
    tasks: list["Task"] = field(default_factory=list)

    def update(self, name: Optional[str] = None, species: Optional[str] = None):
        """Update the pet's name and/or species in place."""
        if name is not None:
            self.name = name
        if species is not None:
            self.species = species

    def add_task(self, task: "Task"):
        """Register a task as belonging to this pet."""
        self.tasks.append(task)


@dataclass
class Owner:
    name: str
    available_minutes: int
    pets: list[Pet]

    def update(self, name: Optional[str] = None, available_minutes: Optional[int] = None):
        """Update the owner's name and/or available minutes in place."""
        if name is not None:
            self.name = name
        if available_minutes is not None:
            self.available_minutes = available_minutes


@dataclass
class Task:
    name: str
    duration: int
    priority: str
    pet: Pet
    recurrence: Optional[str] = None  # "daily", "weekly", or None for one-off
    due_date: Optional[datetime] = None
    completed: bool = False

    def mark_complete(self):
        """Mark this task as completed, spawning the next occurrence if it recurs."""
        self.completed = True
        return self.spawn_next_occurrence()

    def spawn_next_occurrence(self):
        """If this task recurs, create and register the next occurrence."""
        interval = RECURRENCE_INTERVALS.get(self.recurrence) if self.recurrence else None
        if interval is None:
            return None

        base_date = self.due_date or datetime.now()
        next_task = Task(
            name=self.name,
            duration=self.duration,
            priority=self.priority,
            pet=self.pet,
            recurrence=self.recurrence,
            due_date=base_date + interval,
            completed=False,
        )
        self.pet.add_task(next_task)
        return next_task

    def update(
        self,
        name: Optional[str] = None,
        duration: Optional[int] = None,
        priority: Optional[str] = None,
        recurrence: Optional[str] = None,
    ):
        """Update the task's fields in place, skipping any left as None."""
        if name is not None:
            self.name = name
        if duration is not None:
            self.duration = duration
        if priority is not None:
            self.priority = priority
        if recurrence is not None:
            self.recurrence = recurrence


class Scheduler:
    def __init__(self, owner: Owner):
        """Set up a scheduler for the given owner with empty task/plan lists."""
        self.owner = owner
        self.tasks: list[Task] = []
        self.plan: list[Task] = []
        self.skipped: list[Task] = []
        self.conflicts: list[str] = []

    def add_task(self, task: Task):
        """Register a task as a candidate for the daily plan."""
        self.tasks.append(task)

    def filter_tasks(self, completed: Optional[bool] = None, pet_name: Optional[str] = None):
        """Return tasks matching the given completion status and/or pet name."""
        result = self.tasks
        if completed is not None:
            result = [t for t in result if t.completed == completed]
        if pet_name is not None:
            result = [t for t in result if t.pet.name == pet_name]
        return result

    def sort_by_time(self, tasks, descending: bool = True):
        """Sort the given tasks by their duration (time) attribute."""
        return sorted(tasks, key=lambda t: t.duration, reverse=descending)

    def detect_conflicts(self, tasks: Optional[list[Task]] = None):
        """Return warning messages for any tasks that share the exact same due_date."""
        candidates = tasks if tasks is not None else self.tasks
        by_time: dict[datetime, list[Task]] = {}
        for task in candidates:
            if task.due_date is None:
                continue
            by_time.setdefault(task.due_date, []).append(task)

        warnings = []
        for due_date, scheduled in by_time.items():
            if len(scheduled) < 2:
                continue
            names = ", ".join(f"'{t.name}' ({t.pet.name})" for t in scheduled)
            warnings.append(
                f"Conflict at {due_date.strftime('%Y-%m-%d %H:%M')}: {names} are scheduled at the same time."
            )
        return warnings

    def generate_plan(self):
        """Build a plan by fitting tasks, highest priority first, into available time."""
        self.plan = []
        self.skipped = []

        active_tasks = self.filter_tasks(completed=False)
        self.conflicts = self.detect_conflicts(active_tasks)

        ordered = sorted(
            active_tasks,
            key=lambda t: (PRIORITY_ORDER.get(t.priority, len(PRIORITY_ORDER)), -t.duration),
        )

        remaining = self.owner.available_minutes
        for task in ordered:
            if task.duration <= remaining:
                self.plan.append(task)
                remaining -= task.duration
            else:
                self.skipped.append(task)

        return self.plan

    def display_plan(self):
        """Print the generated plan as a timed schedule."""
        if not self.plan:
            print("No tasks scheduled.")
            return

        current_time = datetime.strptime(DAY_START, "%H:%M")
        print(f"Today's Schedule for {self.owner.name}:")
        for task in self.plan:
            print(f"  {current_time.strftime('%H:%M')} — {task.name} for {task.pet.name} "
                  f"({task.duration} min) [priority: {task.priority}]")
            current_time += timedelta(minutes=task.duration)

        for warning in self.conflicts:
            print(f"  WARNING: {warning}")

    def explain_plan(self):
        """Return a human-readable explanation of why each task was included or skipped."""
        lines = []
        for task in self.plan:
            lines.append(
                f"Included '{task.name}' (priority: {task.priority}, "
                f"{task.duration} min) — fit within remaining available time."
            )
        for task in self.skipped:
            lines.append(
                f"Skipped '{task.name}' (priority: {task.priority}, "
                f"{task.duration} min) — not enough time remaining."
            )
        return "\n".join(lines)
