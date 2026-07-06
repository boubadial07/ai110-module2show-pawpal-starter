# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

My initial UML had four classes:

- **Owner** — holds the person's name and email, and manages a list of pets (`add_pet`, `remove_pet`, `view_pets`).
- **Pet** — holds name, species, and age, and manages its own care tasks (`add_task`, `complete_task`, `view_tasks`).
- **Task** — a single care item with a title, due date, priority, and completed flag, plus behavior to `mark_complete` and check `is_overdue`.
- **Scheduler** — the logic class that operates on tasks: `sort_tasks`, `detect_conflicts`, and `get_today_tasks`.

The relationships were: an Owner owns many Pets (1→\*), a Pet has many Tasks (1→\*), and the Scheduler manages Tasks.

**b. Design changes**

Yes, the design changed once I started thinking about what a *daily plan* actually needs:

1. **Added `duration_minutes` to Task.** My original Task couldn't answer "does this fit in the time I have today?" Since the whole point is planning around available time, duration was essential.
2. **Added a `build_plan()` method and a new `DailyPlan` class.** My original Scheduler could sort and filter tasks but never actually *produced a plan*. I added `build_plan(available_minutes)` to select the tasks that fit the budget, and a `DailyPlan` class to hold the scheduled tasks, the skipped tasks, and a plain-language explanation of why.
3. **Changed `due_date` from a string to a real date** so overdue/today checks are reliable instead of comparing strings.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers three things: **available time** (a minutes budget for the day), **priority** (high/medium/high), and **due date** (used to order tasks and to decide what's relevant today). Priority mattered most the essentials like medication and feeding should never be dropped in favor of grooming. So tasks are always sorted highest-priority-first, with due date and duration only breaking ties.

**b. Tradeoffs**

My scheduler uses a **greedy** approach: it walks the priority-sorted list and adds each task that still fits the remaining time, skipping the rest. This isn't guaranteed to be the *optimal* packing. For example, with 15 minutes left it will skip a 20-minute task rather than swap things around to fill every last minute. I think that tradeoff is reasonable here because respecting priority order is more important than squeezing the schedule tight: a pet owner would rather do the important tasks in order than have the app rearrange things unpredictably to save a few minutes. Greedy is also simple to understand and easy to explain to the user, which matters since the app shows its reasoning.

---

## 3. AI Collaboration

**a. How you used AI**

I used AI throughout the project: to review my UML design, to scaffold the class stubs from that UML, to implement the scheduling logic, and to write the test suite. The most helpful prompts were the ones where I shared my own work first. For example, I wrote the initial UML myself and then asked the AI to critique it against the project requirements. That gave me specific, actionable feedback (like "your Task has no duration, so it can't do time-based planning") instead of a generic answer.

**b. Judgment and verification**

The AI suggested several additions to my original design — a `duration_minutes` field, a `build_plan()` method, and a whole new `DailyPlan` class. I didn't just take these on faith; I checked each one against the actual requirement in the README (planning around available time and explaining the plan) and only kept the ones that clearly served that goal. I also verified the implementation rather than trusting it: I ran the full test suite and confirmed all 23 tests passed, and I ran the scheduler on a real set of tasks to see that the output made sense (essentials scheduled first, lower-priority grooming skipped when time ran out).

---

## 4. Testing and Verification

**a. What you tested**

I wrote 23 tests covering every class. The most important ones test the scheduling behavior: that `build_plan` stays within the time budget, prefers high-priority tasks, skips tasks that don't fit, and always returns an explanation. I also tested edge cases like a completed task never counting as overdue, sorting not mutating the original list, and errors being raised for invalid actions (completing a task that isn't the pet's, a negative time budget). These matter because the scheduling logic is the core of the app if it silently picked the wrong tasks, the whole plan would be untrustworthy. I passed fixed dates into the tests so they're deterministic and don't break depending on the day they run.

**b. Confidence**

I'm fairly confident the scheduler works correctly for the cases it's designed for, since all 23 tests pass and they cover the main paths and several edge cases. If I had more time I'd test tasks with equal priority *and* equal due date, very large task lists, and eventually recurring tasks (daily/weekly), which I haven't implemented yet.

---

## 5. Reflection

**a. What went well**

I'm most satisfied with the scheduling logic and how it explains itself. The `build_plan` method doesn't just output a list, it also produces a plain-language explanation of why each task was chosen or skipped, which makes the app feel trustworthy instead of like a black box. I'm also happy that the design flowed cleanly from UML to code to tests.

**b. What you would improve**

If I had another iteration, I'd add recurring tasks (daily/weekly), since real pet care is repetitive and my current model only handles one-off tasks with a due date. I'd also give tasks real start times so the scheduler could detect genuine time-slot overlaps instead of only flagging duplicate titles as conflicts.

**c. Key takeaway**

The biggest thing I learned is that designing the system first, writing the UML before any code, made everything downstream easier, and that the design should be allowed to change once you understand the problem better (like adding `duration` and `DailyPlan` once I realized what a plan actually needs). I also learned that AI is most useful when I bring my own work and judgment to it: it gives better feedback on something I've already attempted, and I still have to verify its output with tests rather than assume it's correct.
