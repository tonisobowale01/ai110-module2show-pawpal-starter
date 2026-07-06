from pawpal_system import Pet, Owner, Task, Scheduler

biscuit = Pet("Biscuit", "Golden Retriever")
whiskers = Pet("Whiskers", "Tabby Cat")

owner = Owner("Alex", available_minutes=90, pets=[biscuit, whiskers])

scheduler = Scheduler(owner)
scheduler.add_task(Task("Morning walk", 30, "high", pet=biscuit))
scheduler.add_task(Task("Feeding", 10, "high", pet=whiskers))
scheduler.add_task(Task("Litter box cleaning", 15, "medium", pet=whiskers))

scheduler.generate_plan()
scheduler.display_plan()
