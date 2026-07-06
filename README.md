# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
Today's Schedule for Alex:
  08:00 — Morning walk for Biscuit (30 min) [priority: high]
  08:30 — Feeding for Whiskers (10 min) [priority: high]
  08:40 — Litter box cleaning for Whiskers (15 min) [priority: medium]
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest tests/test_pawpal.py -v

# Run with coverage:
pytest --cov
```

Sample test output:

```
============= test session starts =============
platform win32 -- Python 3.14.0, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\tonis\Documents\ai110-module2show-pawpal-starter
plugins: anyio-4.14.0
collected 15 items                             

tests\test_pawpal.py ...............     [100%]

============= 15 passed in 0.06s ==============
```

The suite in `tests/test_pawpal.py` covers:

- **Task completion & recurrence** — completing a task flips its status; a `"daily"`/`"weekly"` recurring task spawns its next occurrence with the due date advanced by 1 or 7 days; one-off tasks (`recurrence=None`) and unknown recurrence values don't spawn anything.
- **Sorting** — `sort_by_time()` orders tasks by duration (descending) with stable tie-breaking; `sort_by_due_date()` orders tasks chronologically and pushes undated tasks to the end without crashing.
- **Plan generation** — `generate_plan()` respects the owner's available minutes (skipping tasks that don't fit), prioritizes higher-priority tasks when time is limited, excludes already-completed tasks, handles an empty task list, and pushes unrecognized priority values to the back of the queue instead of erroring.
- **Conflict detection** — `detect_conflicts()` flags multiple tasks sharing the same `due_date` and ignores tasks with no `due_date` set (so they aren't falsely treated as conflicting with each other).

### Confidence level

**⭐⭐⭐⭐☆ (4/5)**

All 15 tests pass, covering the core scheduling behaviors (sorting, plan generation, recurrence, conflict detection) plus their main edge cases (empty inputs, ties, unknown priority/recurrence values, missing due dates). This gives good confidence in the correctness of the scheduling and recurrence logic as implemented, short of a 5th star due to the gaps below.

Known gaps not covered by tests:
- `spawn_next_occurrence()` falls back to `datetime.now()` when `due_date` is `None`, which is non-deterministic and untested.
- No tests exercise the Streamlit UI (`app.py`) itself — only the underlying `pawpal_system.py` logic.
- No tests for negative/zero `duration` or `available_minutes` values.

## 📐 Smarter Scheduling

| Feature           | Method(s)                                                  | Notes                                                                                                                                                                                                                                                         |
| ----------------- | ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Task sorting      | `Scheduler.sort_by_time()`, `Scheduler.generate_plan()`    | `generate_plan()` sorts candidate tasks by priority first, then by duration (longest first) as a tie-break, and greedily packs them into the owner's available minutes. `sort_by_time()` is also exposed standalone to sort any task list purely by duration. |
| Filtering         | `Scheduler.filter_tasks()`                                 | Filters tasks by completion status and/or pet name. `generate_plan()` uses it internally to exclude completed tasks before scheduling.                                                                                                                        |
| Conflict handling | `Scheduler.detect_conflicts()`, `Scheduler.display_plan()` | Groups tasks by exact `due_date` and returns a warning string for any timestamp shared by 2+ tasks (same or different pets), instead of crashing. `generate_plan()` populates `self.conflicts`, and `display_plan()` prints each warning after the schedule.  |
| Recurring tasks   | `Task.mark_complete()`, `Task.spawn_next_occurrence()`     | Completing a task with `recurrence` set to `"daily"` or `"weekly"` automatically creates and registers (via `Pet.add_task()`) the next occurrence, with `due_date` advanced by 1 or 7 days respectively.                                                      |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
