"""Tests for the PawPal+ core system.

Dates are passed explicitly (never date.today()) so these tests are
deterministic regardless of when they run.
"""

from datetime import date

import pytest

from pawpal_system import DailyPlan, Owner, Pet, Scheduler, Task


TODAY = date(2026, 7, 5)
YESTERDAY = date(2026, 7, 4)
TOMORROW = date(2026, 7, 6)


# --------------------------------------------------------------------------- #
# Task
# --------------------------------------------------------------------------- #
def test_mark_complete():
    task = Task("Walk", 20, "high")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_is_overdue_past_due_and_incomplete():
    task = Task("Meds", 5, "high", due_date=YESTERDAY)
    assert task.is_overdue(today=TODAY) is True


def test_is_overdue_future_due_is_not_overdue():
    task = Task("Grooming", 30, "low", due_date=TOMORROW)
    assert task.is_overdue(today=TODAY) is False


def test_completed_task_is_never_overdue():
    task = Task("Meds", 5, "high", due_date=YESTERDAY, completed=True)
    assert task.is_overdue(today=TODAY) is False


def test_task_without_due_date_is_not_overdue():
    task = Task("Play", 15, "medium")
    assert task.is_overdue(today=TODAY) is False


# --------------------------------------------------------------------------- #
# Pet
# --------------------------------------------------------------------------- #
def test_add_and_view_tasks():
    pet = Pet("Mochi", "cat")
    task = Task("Feed", 10, "high")
    pet.add_task(task)
    assert pet.view_tasks() == [task]


def test_complete_task_marks_it_done():
    pet = Pet("Mochi", "cat")
    task = Task("Feed", 10, "high")
    pet.add_task(task)
    pet.complete_task(task)
    assert task.completed is True


def test_complete_foreign_task_raises():
    pet = Pet("Mochi", "cat")
    stray = Task("Feed", 10, "high")
    with pytest.raises(ValueError):
        pet.complete_task(stray)


def test_view_tasks_returns_a_copy():
    pet = Pet("Mochi", "cat")
    pet.add_task(Task("Feed", 10))
    pet.view_tasks().clear()
    assert len(pet.view_tasks()) == 1


# --------------------------------------------------------------------------- #
# Owner
# --------------------------------------------------------------------------- #
def test_add_and_view_pets():
    owner = Owner("Jordan", "jordan@example.com")
    pet = Pet("Mochi", "cat")
    owner.add_pet(pet)
    assert owner.view_pets() == [pet]


def test_remove_pet():
    owner = Owner("Jordan")
    pet = Pet("Mochi", "cat")
    owner.add_pet(pet)
    owner.remove_pet(pet)
    assert owner.view_pets() == []


def test_remove_unowned_pet_raises():
    owner = Owner("Jordan")
    with pytest.raises(ValueError):
        owner.remove_pet(Pet("Ghost", "dog"))


# --------------------------------------------------------------------------- #
# Scheduler.sort_tasks
# --------------------------------------------------------------------------- #
def test_sort_orders_by_priority():
    low = Task("Groom", 30, "low")
    high = Task("Meds", 5, "high")
    medium = Task("Walk", 20, "medium")
    scheduler = Scheduler([low, high, medium])
    assert scheduler.sort_tasks() == [high, medium, low]


def test_sort_breaks_priority_ties_by_due_date_then_duration():
    later = Task("A", 20, "high", due_date=TOMORROW)
    sooner = Task("B", 20, "high", due_date=TODAY)
    no_date_short = Task("C", 5, "high")
    scheduler = Scheduler([no_date_short, later, sooner])
    # sooner due date first; the undated task sorts last despite being shortest
    assert scheduler.sort_tasks() == [sooner, later, no_date_short]


def test_sort_does_not_mutate_original():
    tasks = [Task("Groom", 30, "low"), Task("Meds", 5, "high")]
    scheduler = Scheduler(tasks)
    scheduler.sort_tasks()
    assert tasks[0].title == "Groom"  # original order untouched


# --------------------------------------------------------------------------- #
# Scheduler.detect_conflicts
# --------------------------------------------------------------------------- #
def test_detect_conflicts_finds_duplicate_titles():
    a = Task("Walk", 20, "high")
    b = Task("walk ", 30, "low")  # same title, different case/whitespace
    scheduler = Scheduler([a, b])
    assert scheduler.detect_conflicts() == [(a, b)]


def test_no_conflicts_for_distinct_titles():
    scheduler = Scheduler([Task("Walk", 20), Task("Feed", 10)])
    assert scheduler.detect_conflicts() == []


# --------------------------------------------------------------------------- #
# Scheduler.get_today_tasks
# --------------------------------------------------------------------------- #
def test_get_today_tasks_filters_and_orders():
    done = Task("Done", 10, "high", completed=True)
    future = Task("Future", 10, "high", due_date=TOMORROW)
    overdue = Task("Overdue", 10, "high", due_date=YESTERDAY)
    anytime = Task("Anytime", 10, "medium")
    scheduler = Scheduler([done, future, overdue, anytime])
    today = scheduler.get_today_tasks(today=TODAY)
    # completed and future-dated tasks excluded; overdue (high) before anytime (medium)
    assert today == [overdue, anytime]


# --------------------------------------------------------------------------- #
# Scheduler.build_plan
# --------------------------------------------------------------------------- #
def test_build_plan_fits_within_budget():
    scheduler = Scheduler(
        [Task("Walk", 30, "high"), Task("Feed", 10, "high"), Task("Groom", 45, "low")]
    )
    plan = scheduler.build_plan(available_minutes=40, today=TODAY)
    assert isinstance(plan, DailyPlan)
    assert plan.total_minutes <= 40


def test_build_plan_prefers_high_priority():
    high = Task("Meds", 20, "high")
    low = Task("Groom", 20, "low")
    scheduler = Scheduler([low, high])
    plan = scheduler.build_plan(available_minutes=20, today=TODAY)
    assert plan.scheduled == [high]
    assert low in plan.skipped


def test_build_plan_skips_tasks_that_dont_fit():
    scheduler = Scheduler([Task("LongWalk", 90, "high")])
    plan = scheduler.build_plan(available_minutes=30, today=TODAY)
    assert plan.scheduled == []
    assert len(plan.skipped) == 1


def test_build_plan_has_explanation():
    scheduler = Scheduler([Task("Walk", 20, "high")])
    plan = scheduler.build_plan(available_minutes=60, today=TODAY)
    assert "Walk" in plan.explanation
    assert plan.explanation.strip() != ""


def test_build_plan_negative_budget_raises():
    scheduler = Scheduler([Task("Walk", 20)])
    with pytest.raises(ValueError):
        scheduler.build_plan(available_minutes=-5, today=TODAY)
