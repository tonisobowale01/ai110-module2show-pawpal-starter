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

- If yes, describe at least one change and why you made it.
  
  > Yes. An early draft included a fifth class called `Schedule` to act as a result container for the generated plan. This was removed to keep the design at four classes — `Scheduler` absorbed that responsibility by storing the plan internally as a `plan` list attribute. This kept the design simpler without losing any required functionality.
  
  > A second change was the relationship between `Owner` and `Pet`. They were initially modeled as a loose association, but were tightened to **composition** — `Pet` is an attribute of `Owner` — because the scenario has exactly one pet per owner and it made no sense for a pet to exist without an owner in this system.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
