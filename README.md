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

Given these tasks and **60 minutes** available, PawPal+ selects the highest-priority
tasks that fit the time budget and explains its choices:

```
Daily plan for Biscuit (Golden Retriever) — 60 min available:

  Give medication (5 min) [priority: high]
  Feeding (10 min) [priority: high]
  Morning walk (30 min) [priority: high]

Planned 3 task(s) within a 60-minute budget (45 min used, 15 min free).
  • Give medication (5 min) — chosen: high priority.
  • Feeding (10 min) — chosen: high priority.
  • Morning walk (30 min) — chosen: high priority.
  • Skipped Play/enrichment (20 min) — medium priority, didn't fit remaining time.
  • Skipped Grooming (45 min) — low priority, didn't fit remaining time.
```

Note that `Play/enrichment` (20 min) is skipped even though 15 minutes remain — it
doesn't fit — and the lower-priority `Grooming` is dropped so the essentials fit first.

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
============================= test session starts =============================
platform win32 -- Python 3.12.5, pytest-9.1.1, pluggy-1.6.0
collected 23 items

tests/test_pawpal_system.py::test_mark_complete PASSED                   [  4%]
tests/test_pawpal_system.py::test_is_overdue_past_due_and_incomplete PASSED [  8%]
tests/test_pawpal_system.py::test_is_overdue_future_due_is_not_overdue PASSED [ 13%]
tests/test_pawpal_system.py::test_completed_task_is_never_overdue PASSED [ 17%]
tests/test_pawpal_system.py::test_task_without_due_date_is_not_overdue PASSED [ 21%]
tests/test_pawpal_system.py::test_add_and_view_tasks PASSED              [ 26%]
tests/test_pawpal_system.py::test_complete_task_marks_it_done PASSED     [ 30%]
tests/test_pawpal_system.py::test_complete_foreign_task_raises PASSED    [ 34%]
tests/test_pawpal_system.py::test_view_tasks_returns_a_copy PASSED       [ 39%]
tests/test_pawpal_system.py::test_add_and_view_pets PASSED               [ 43%]
tests/test_pawpal_system.py::test_remove_pet PASSED                      [ 47%]
tests/test_pawpal_system.py::test_remove_unowned_pet_raises PASSED       [ 52%]
tests/test_pawpal_system.py::test_sort_orders_by_priority PASSED         [ 56%]
tests/test_pawpal_system.py::test_sort_breaks_priority_ties_by_due_date_then_duration PASSED [ 60%]
tests/test_pawpal_system.py::test_sort_does_not_mutate_original PASSED   [ 65%]
tests/test_pawpal_system.py::test_detect_conflicts_finds_duplicate_titles PASSED [ 69%]
tests/test_pawpal_system.py::test_no_conflicts_for_distinct_titles PASSED [ 73%]
tests/test_pawpal_system.py::test_get_today_tasks_filters_and_orders PASSED [ 78%]
tests/test_pawpal_system.py::test_build_plan_fits_within_budget PASSED   [ 82%]
tests/test_pawpal_system.py::test_build_plan_prefers_high_priority PASSED [ 86%]
tests/test_pawpal_system.py::test_build_plan_skips_tasks_that_dont_fit PASSED [ 91%]
tests/test_pawpal_system.py::test_build_plan_has_explanation PASSED      [ 95%]
tests/test_pawpal_system.py::test_build_plan_negative_budget_raises PASSED [100%]

============================= 23 passed in 0.08s ==============================
```

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_tasks()` | Orders by priority (high→low), then soonest `due_date`, then shortest `duration_minutes` as a tiebreaker. Non-mutating. |
| Filtering | `Scheduler.get_today_tasks()`, `Scheduler.build_plan()` | `get_today_tasks` drops completed and future-dated tasks; `build_plan` greedily skips any task that doesn't fit the remaining time budget. |
| Conflict handling | `Scheduler.detect_conflicts()` | Flags duplicate tasks by matching titles (case- and whitespace-insensitive). The model has no start times, so a repeated task is the meaningful conflict. |
| Recurring tasks | — | Not implemented. Tasks are one-off with an optional `due_date`. A future `RecurringTask` subclass (daily/weekly) would extend this. |

## 📸 Demo Walkthrough

Run the app with `streamlit run app.py`, then:

1. Enter the owner name, pet name, and species at the top.
2. Add tasks one at a time — each with a title, duration (minutes), and priority (low/medium/high). Added tasks appear in the "Current tasks" table.
3. Set **Time available today (minutes)** to your daily budget (e.g. 60).
4. Click **Generate schedule**. PawPal+ sorts tasks by priority and packs the ones that fit into your time budget.
5. Review the results: a table of scheduled tasks, a list of any skipped tasks, and a "Why this plan?" expander that explains each choice.

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
