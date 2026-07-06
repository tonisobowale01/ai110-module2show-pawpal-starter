from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Optional

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}
DAY_START = "08:00"


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
    recurring: bool = False
    completed: bool = False

    def mark_complete(self):
        """Mark this task as completed."""
        self.completed = True

    def update(
        self,
        name: Optional[str] = None,
        duration: Optional[int] = None,
        priority: Optional[str] = None,
        recurring: Optional[bool] = None,
    ):
        """Update the task's fields in place, skipping any left as None."""
        if name is not None:
            self.name = name
        if duration is not None:
            self.duration = duration
        if priority is not None:
            self.priority = priority
        if recurring is not None:
            self.recurring = recurring


class Scheduler:
    def __init__(self, owner: Owner):
        """Set up a scheduler for the given owner with empty task/plan lists."""
        self.owner = owner
        self.tasks: list[Task] = []
        self.plan: list[Task] = []
        self.skipped: list[Task] = []

    def add_task(self, task: Task):
        """Register a task as a candidate for the daily plan."""
        self.tasks.append(task)

    def generate_plan(self):
        """Build a plan by fitting tasks, highest priority first, into available time."""
        self.plan = []
        self.skipped = []

        ordered = sorted(
            self.tasks,
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
