from datetime import datetime

from pawpal_system import Owner, Pet, Scheduler, Task


def test_mark_complete_changes_status():
    pet = Pet("Biscuit", "Golden Retriever")
    task = Task("Feeding", 10, "high", pet=pet)

    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_adding_task_increases_pet_task_count():
    pet = Pet("Biscuit", "Golden Retriever")

    assert len(pet.tasks) == 0
    pet.add_task(Task("Walk", 30, "high", pet=pet))
    assert len(pet.tasks) == 1


def test_mark_complete_spawns_next_occurrence_for_recurring_task():
    pet = Pet("Biscuit", "Golden Retriever")
    due = datetime(2026, 1, 1, 8, 0)
    task = Task("Feeding", 10, "high", pet=pet, recurrence="daily", due_date=due)
    pet.add_task(task)

    next_task = task.mark_complete()

    assert next_task is not None
    assert next_task.due_date == datetime(2026, 1, 2, 8, 0)
    assert next_task.completed is False
    assert next_task in pet.tasks


def test_mark_complete_does_not_spawn_for_one_off_task():
    pet = Pet("Biscuit", "Golden Retriever")
    task = Task("Vet visit", 30, "high", pet=pet, recurrence=None)

    next_task = task.mark_complete()

    assert next_task is None
    assert len(pet.tasks) == 0


def test_spawn_next_occurrence_ignores_unknown_recurrence_value():
    pet = Pet("Biscuit", "Golden Retriever")
    task = Task("Grooming", 20, "medium", pet=pet, recurrence="monthly")

    next_task = task.spawn_next_occurrence()

    assert next_task is None


def test_sort_by_time_orders_tasks_by_duration_descending():
    pet = Pet("Biscuit", "Golden Retriever")
    owner = Owner("Alex", available_minutes=60, pets=[pet])
    scheduler = Scheduler(owner)

    short = Task("Feed", 5, "low", pet=pet)
    medium = Task("Walk", 20, "low", pet=pet)
    long = Task("Groom", 45, "low", pet=pet)

    ordered = scheduler.sort_by_time([medium, short, long])

    assert ordered == [long, medium, short]


def test_sort_by_time_handles_equal_durations_stably():
    pet = Pet("Biscuit", "Golden Retriever")
    owner = Owner("Alex", available_minutes=60, pets=[pet])
    scheduler = Scheduler(owner)

    first = Task("Feed", 10, "low", pet=pet)
    second = Task("Walk", 10, "low", pet=pet)

    ordered = scheduler.sort_by_time([first, second])

    assert ordered == [first, second]


def test_generate_plan_skips_task_that_exceeds_available_minutes():
    pet = Pet("Biscuit", "Golden Retriever")
    owner = Owner("Alex", available_minutes=10, pets=[pet])
    scheduler = Scheduler(owner)
    task = Task("Long groom", 30, "high", pet=pet)
    scheduler.add_task(task)

    plan = scheduler.generate_plan()

    assert plan == []
    assert task in scheduler.skipped


def test_generate_plan_prioritizes_high_priority_first():
    pet = Pet("Biscuit", "Golden Retriever")
    owner = Owner("Alex", available_minutes=15, pets=[pet])
    scheduler = Scheduler(owner)
    low = Task("Play", 10, "low", pet=pet)
    high = Task("Feed", 10, "high", pet=pet)
    scheduler.add_task(low)
    scheduler.add_task(high)

    plan = scheduler.generate_plan()

    assert plan == [high]
    assert low in scheduler.skipped


def test_generate_plan_excludes_completed_tasks():
    pet = Pet("Biscuit", "Golden Retriever")
    owner = Owner("Alex", available_minutes=60, pets=[pet])
    scheduler = Scheduler(owner)
    completed_task = Task("Feed", 10, "high", pet=pet, completed=True)
    scheduler.add_task(completed_task)

    plan = scheduler.generate_plan()

    assert plan == []
    assert completed_task not in scheduler.skipped


def test_generate_plan_with_no_tasks_produces_empty_plan():
    pet = Pet("Biscuit", "Golden Retriever")
    owner = Owner("Alex", available_minutes=60, pets=[pet])
    scheduler = Scheduler(owner)

    plan = scheduler.generate_plan()

    assert plan == []
    assert scheduler.skipped == []


def test_detect_conflicts_flags_tasks_at_same_due_date():
    pet_a = Pet("Biscuit", "Golden Retriever")
    pet_b = Pet("Milo", "Beagle")
    owner = Owner("Alex", available_minutes=60, pets=[pet_a, pet_b])
    scheduler = Scheduler(owner)
    due = datetime(2026, 1, 1, 8, 0)
    task_a = Task("Feed", 10, "high", pet=pet_a, due_date=due)
    task_b = Task("Walk", 15, "high", pet=pet_b, due_date=due)
    scheduler.add_task(task_a)
    scheduler.add_task(task_b)

    warnings = scheduler.detect_conflicts()

    assert len(warnings) == 1
    assert "Feed" in warnings[0] and "Walk" in warnings[0]


def test_detect_conflicts_ignores_tasks_without_due_date():
    pet = Pet("Biscuit", "Golden Retriever")
    owner = Owner("Alex", available_minutes=60, pets=[pet])
    scheduler = Scheduler(owner)
    task_a = Task("Feed", 10, "high", pet=pet, due_date=None)
    task_b = Task("Walk", 15, "high", pet=pet, due_date=None)
    scheduler.add_task(task_a)
    scheduler.add_task(task_b)

    warnings = scheduler.detect_conflicts()

    assert warnings == []


def test_sort_by_due_date_orders_tasks_chronologically():
    pet = Pet("Biscuit", "Golden Retriever")
    owner = Owner("Alex", available_minutes=60, pets=[pet])
    scheduler = Scheduler(owner)

    early = Task("Feed", 10, "low", pet=pet, due_date=datetime(2026, 1, 1, 8, 0))
    late = Task("Walk", 10, "low", pet=pet, due_date=datetime(2026, 1, 2, 8, 0))
    undated = Task("Groom", 10, "low", pet=pet, due_date=None)

    ordered = scheduler.sort_by_due_date([late, undated, early])

    assert ordered == [early, late, undated]


def test_generate_plan_with_unknown_priority_is_scheduled_last():
    pet = Pet("Biscuit", "Golden Retriever")
    owner = Owner("Alex", available_minutes=100, pets=[pet])
    scheduler = Scheduler(owner)
    unknown_priority = Task("Mystery", 10, "urgent", pet=pet)
    known_priority = Task("Feed", 10, "low", pet=pet)
    scheduler.add_task(unknown_priority)
    scheduler.add_task(known_priority)

    plan = scheduler.generate_plan()

    assert plan == [known_priority, unknown_priority]
