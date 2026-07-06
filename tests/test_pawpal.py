from pawpal_system import Pet, Task


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
