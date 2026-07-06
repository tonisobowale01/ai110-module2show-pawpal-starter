from datetime import datetime
from pawpal_system import Pet, Owner, Task, Scheduler

biscuit = Pet("Biscuit", "Golden Retriever")
whiskers = Pet("Whiskers", "Tabby Cat")

owner = Owner("Alex", available_minutes=90, pets=[biscuit, whiskers])

scheduler = Scheduler(owner)
same_time = datetime(2026, 7, 5, 8, 0)
scheduler.add_task(Task("Morning walk", 30, "high", pet=biscuit, due_date=same_time))
scheduler.add_task(Task("Feeding", 10, "high", pet=whiskers, due_date=same_time))
scheduler.add_task(Task("Feeding", 10, "high", pet=biscuit))
scheduler.add_task(Task("Litter box cleaning", 15, "medium", pet=whiskers))

vet_visit = Task("Vet checkup", 60, "low", pet=biscuit)
vet_visit.mark_complete()
scheduler.add_task(vet_visit)

print("All tasks for Biscuit:")
for t in scheduler.filter_tasks(pet_name="Biscuit"):
    print(f"  {t.name} (completed={t.completed})")

print("\nIncomplete tasks only:")
for t in scheduler.filter_tasks(completed=False):
    print(f"  {t.name} (priority={t.priority})")

print("\nGenerating plan (should skip completed 'Vet checkup' and sort high-priority first):")
scheduler.generate_plan()
scheduler.display_plan()

print("\n" + scheduler.explain_plan())
