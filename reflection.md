# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
  
  > The initial design centered on four classes: `Pet`, `Owner`, `Task`, and `Scheduler`. The goal was to model a daily pet care planner where an owner's available time acts as the core scheduling constraint.

- What classes did you include, and what responsibilities did you assign to each?
  
  - **`Pet`** — a pure data class holding the animal's name and species. It has no behavior beyond an `update()` method for editing its fields.
  - **`Owner`** — a data class that composes a `Pet` (composition relationship) and tracks the owner's name and how many minutes they have available that day. Also editable via `update()`.
  - **`Task`** — a data class representing a single care item (walk, feeding, medication, etc.) with a name, duration in minutes, priority level, and a recurring flag for daily vs. one-off tasks. Editable via `update()`.
  - **`Scheduler`** — the only class with real behavior. It holds a reference to an `Owner` and aggregates a list of `Task` objects. It is responsible for generating the daily plan (`generate_plan()`), displaying it (`display_plan()`), and explaining the reasoning behind it (`explain_plan()`).

**b. Design changes**

- Did your design change during implementation?

  > Yes, twice — both times because the initial design turned out to be more restrictive than the scenario actually needed once real usage (the CLI demo in `main.py` and the Streamlit UI in `app.py`) put pressure on it.

- If yes, describe at least one change and why you made it.
  
  > Yes. An early draft included a fifth class called `Schedule` to act as a result container for the generated plan. This was removed to keep the design at four classes — `Scheduler` absorbed that responsibility by storing the plan internally as a `plan` list attribute. This kept the design simpler without losing any required functionality.
  
  > A second, larger change was the `Owner`–`Pet` relationship. It started as a single `Owner.pet: Pet` composition (one pet per owner), which matched the initial assumption that the scenario only needed one animal. That broke down as soon as we tried to build a realistic demo with an owner caring for two pets (`Biscuit` and `Whiskers`) — `Owner.pet` became `Owner.pets: list[Pet]`, and `Task` gained its own `pet: Pet` field so each task could be tied to whichever pet it actually belongs to, instead of assuming the owner's one-and-only pet. The Streamlit UI later needed the same flexibility (an "Add pet" flow plus a per-task pet selector), which confirmed the list-based design was the right call.
  
  > A third change was extending `Task` well beyond the original `recurring: bool` flag: it grew a `recurrence: Optional[str]` (`"daily"`/`"weekly"`/`None`), a `due_date`, and a `completed` flag with a `mark_complete()` method that automatically spawns the next occurrence for recurring tasks. `Pet` also grew its own `tasks` list and `add_task()` method, and `Scheduler` grew `filter_tasks()`, `sort_by_time()`, `sort_by_due_date()`, and `detect_conflicts()` to support the richer task model. None of this existed in the original four-class sketch — it emerged from iterating on what the UI and CLI demo needed to actually be useful.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?

  > Two hard constraints and one soft one. The hard constraints are **time** (`Owner.available_minutes` — the total budget `generate_plan()` packs tasks into) and **completion status** (`filter_tasks(completed=False)` excludes anything already done before scheduling even starts). The soft constraint is **priority** (`"high"`/`"medium"`/`"low"`), which determines the order tasks are considered in, with duration as a tie-breaker. Later we also added **due-date conflicts** as an informational constraint — `detect_conflicts()` doesn't block scheduling, it just surfaces a warning when two tasks share the same exact due date.

- How did you decide which constraints mattered most?

  > Time had to be a hard constraint because it's the whole premise of the scenario — a busy owner has a fixed amount of time and the plan can't just assume unlimited minutes. Priority mattered next because the scenario explicitly calls out that some care tasks (feeding, meds) are more critical than others (grooming, enrichment) — a plan that fills time with low-priority tasks while dropping a high-priority one would defeat the purpose of the assistant. We treated conflicts as informational rather than blocking because pet-care schedules in real life often do have simultaneous tasks (e.g., two pets both needing attention at 8am), and refusing to generate a plan over that felt less useful than just flagging it.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

  > `generate_plan()` uses a greedy strategy: tasks are sorted by priority (then by longest duration as a tie-break) and packed into the owner's available minutes in that order, stopping each task the moment it no longer fits. This is not guaranteed to produce the schedule that uses the owner's time most efficiently — a classic counterexample is a knapsack-style case where skipping one large task in favor of several smaller ones would leave less time wasted. An optimal solution would require exploring combinations of tasks (e.g., dynamic programming over available minutes), which is considerably more complex and slower for a real-time planner. The greedy approach was chosen because it's simple to read, fast (single sort plus a linear pass), and produces "good enough" plans that always respect priority ordering — which matters more to a pet owner than squeezing in a couple of extra minutes of usage. It also detects scheduling conflicts (`detect_conflicts()`) as a lightweight warning rather than blocking plan generation, trading strict correctness (no double-booking) for simplicity and not crashing on messy input.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?

  > AI (Claude Code) was used across nearly the whole lifecycle: implementing the method bodies for the original `Pet`/`Owner`/`Task`/`Scheduler` skeleton, extending the design to support multiple pets per owner, writing pytest tests (starting from two targeted tests — `mark_complete()` and pet task counts — before the suite grew), wiring the backend classes into the Streamlit UI (`app.py`) with `st.session_state`, debugging a real UI bug (task tables not stretching to full width), and drafting/updating documentation (`README.md` features list and demo walkthrough, the final UML diagram, and this reflection).

- What kinds of prompts or questions were most helpful?

  > The most productive prompts asked for an explanation or a walkthrough *before* asking for a change — e.g., "walk me through the core implementation" and "check if app.py is implemented right" surfaced real gaps (missing `available_minutes` input, a single-pet limitation, dead UI code for conflict detection) before more code got built on top of them. Narrow, concrete asks ("draft two simple tests for X and Y, wait for confirmation") also worked well because they made it easy to catch a design gap (no `completed`/`mark_complete` existed yet) before implementation started.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.

  > When asked to seed the pet list with a default `Pet("Mochi", "dog")` so the demo wasn't empty on first load, the AI added it automatically. That was rejected — a freshly loaded session shouldn't silently fabricate data the user never asked for, so the default was removed in favor of an explicit "Add a pet before adding tasks" empty state.

- How did you evaluate or verify what the AI suggested?

  > Suggestions that touched runtime behavior were checked by actually running the code rather than trusting the explanation — e.g., when a `st.dataframe(..., width=True)` call was suspected of not stretching to full width, the fix wasn't just re-typed from memory; `inspect.signature(st.dataframe)` was run against the installed Streamlit version to confirm `width` actually expects the string `"stretch"`, not a boolean, before changing the code. Similarly, `main.py` and `streamlit run app.py` were both executed after changes to confirm there were no runtime errors, not just that the syntax parsed.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?

  > The suite in `tests/test_pawpal.py` (15 tests) covers: task completion and recurrence (completing a task flips `completed`, a `"daily"`/`"weekly"` recurring task spawns its next occurrence with the due date advanced correctly, one-off and unknown-recurrence tasks don't spawn anything); sorting (`sort_by_time()` and `sort_by_due_date()`, including stable tie-breaking and undated tasks sorting last); plan generation (`generate_plan()` respects available minutes, prioritizes correctly under time pressure, excludes completed tasks, handles an empty task list, and doesn't error on unrecognized priority values); and conflict detection (`detect_conflicts()` flags shared due dates and ignores undated tasks).

- Why were these tests important?

  > These are the behaviors the entire scenario depends on — if `generate_plan()` didn't respect available time or priority ordering, the app wouldn't be doing its one job. The edge cases (empty task list, ties, unknown priority/recurrence, missing due dates) mattered because a planning tool needs to degrade gracefully on messy input rather than crash, since real usage will inevitably hit them (e.g., a user leaving a due date blank).

**b. Confidence**

- How confident are you that your scheduler works correctly?

  > ⭐⭐⭐⭐☆ (4/5). All 15 tests pass, covering the core scheduling behaviors and their main edge cases, which gives good confidence in the sorting, filtering, plan generation, and recurrence logic as implemented.

- What edge cases would you test next if you had more time?

  > `spawn_next_occurrence()` falls back to `datetime.now()` when a recurring task has no `due_date`, which is non-deterministic and currently untested. There are also no tests exercising negative or zero `duration`/`available_minutes` values, and no automated tests for the Streamlit UI itself (`app.py`) — only the underlying `pawpal_system.py` logic is covered.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

  > The `explain_plan()` feature — turning the scheduler's decisions into a plain-language explanation of why each task was included or skipped. It's a small method, but it's the difference between a scheduler that just spits out a list and one that's actually trustworthy to a user who wants to understand why their dog's walk got bumped.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

  > The greedy scheduling algorithm is the clearest candidate. It always respects priority order but isn't guaranteed to use available time optimally — a knapsack-style dynamic-programming approach could pack tasks more efficiently in edge cases where a large task blocks several smaller ones that would've fit better. I'd also want to add UI-level tests (the current suite only covers `pawpal_system.py`, not `app.py`) and handle negative/zero duration and available-minutes inputs explicitly instead of leaving them untested.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

  > A four-class design that looks complete on day one rarely survives contact with a real UI or CLI demo — the `Owner`–`Pet` cardinality and the `Task` model both changed shape once actual usage (multiple pets, recurring tasks, due dates) put pressure on the original assumptions. The UML and this reflection are more useful written *after* that pressure-testing than before it. Working with AI reinforced the same lesson at a smaller scale: an AI-suggested fix or default (like the `width=True` Streamlit bug, or auto-seeding a demo pet) is only trustworthy once it's actually run and checked against the real API or the user's actual intent, not just read and accepted.
