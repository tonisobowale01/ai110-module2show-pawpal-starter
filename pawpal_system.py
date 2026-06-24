from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Pet:
    name: str
    species: str

    def update(self, name: Optional[str] = None, species: Optional[str] = None):
        pass


@dataclass
class Owner:
    name: str
    available_minutes: int
    pet: Pet

    def update(self, name: Optional[str] = None, available_minutes: Optional[int] = None):
        pass


@dataclass
class Task:
    name: str
    duration: int
    priority: str
    recurring: bool = False

    def update(self, name: Optional[str] = None, duration: Optional[int] = None, priority: Optional[str] = None, recurring: Optional[bool] = None):
        pass


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner
        self.tasks: list[Task] = []
        self.plan: list[Task] = []

    def add_task(self, task: Task):
        pass

    def generate_plan(self):
        pass

    def display_plan(self):
        pass

    def explain_plan(self):
        pass
