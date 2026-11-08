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
============================================================
  Today's Schedule for Yunus's pets
============================================================
  07:30 - 08:00   Loki   Morning walk       [high]
  08:00 - 08:10   Luna   Breakfast          [high]
  08:10 - 08:15   Loki   Heartworm pill     [high]
  08:15 - 08:25   Luna   Clean litter box   [medium]
  08:25 - 08:45   Luna   Play session       [medium]
------------------------------------------------------------
  Time used: 75 of 75 minutes

  Not scheduled today:
    - Loki: Brush coat (needs 15 min but only 0 min left)
============================================================
```

## 🧪 Testing PawPal+

Run the full test suite from the project root:

```bash
python -m pytest
```

The 22 tests in `tests/test_pawpal.py` use a fixed date, so results don't depend on the day you run them. They cover:

- **Basic behavior:** marking a task complete, adding tasks to a pet, rejecting invalid tasks (zero duration, unknown priority, impossible times) and duplicate pet names.
- **Sorting:** `sort_by_time()` returns tasks in chronological order, handles unpadded hours like `"8:00"`, and puts untimed tasks last; the daily plan places high-priority tasks first with correct start times.
- **Filtering and time budget:** filtering by pet and completion status, skipping tasks that don't fit the available minutes, an empty plan for a pet with no tasks, and overdue tasks still being scheduled.
- **Recurring tasks:** completing a daily task creates a copy due the next day, weekly tasks repeat in 7 days, dates roll over month ends, one-time tasks don't repeat, tomorrow's copy stays out of today's plan, and completing an unknown task fails safely.
- **Conflict detection:** same-time tasks are flagged for the same pet and for different pets, partial overlaps are flagged, back-to-back tasks are not, and completed tasks are ignored.

Sample test output:

```
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.2.0, pluggy-1.7.0
rootdir: /mnt/user-data/outputs
configfile: pytest.ini
testpaths: tests
plugins: platformdirs-4.13.0, anyio-4.16.0
collected 22 items

tests/test_pawpal.py ......................                              [100%]

============================== 22 passed in 0.02s ==============================
```

**Confidence level: ★★★★☆ (4/5)**

All core scheduling behaviors pass, including the main edge cases for sorting, recurrence, and conflicts. I'm holding back one star because the Streamlit UI is only tested by hand, conflict detection warns but doesn't resolve clashes, and some cases aren't covered yet, such as tasks running past midnight or two open tasks with the same title on the same pet.

## 📐 Smarter Scheduling

All scheduling logic lives in `pawpal_system.py`. The `Scheduler` reads every task through `Owner.get_all_tasks()`, which returns `(pet, task)` pairs so each result knows which pet it belongs to.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_tasks()`, `Scheduler.sort_by_time()` | Plan order: priority, then preferred time, then shortest first. Time view: due date, then "HH:MM", untimed tasks last |
| Filtering | `Scheduler.filter_tasks()`, `Scheduler.get_pending_tasks()`, `Task.is_due()` | Filter by pet name and/or completion status; the plan only uses unfinished tasks due today or earlier, and skips tasks that don't fit the time left |
| Conflict handling | `Scheduler.detect_conflicts()` | Flags overlapping time windows for the same pet or different pets; returns warnings instead of raising errors |
| Recurring tasks | `Task.next_occurrence()`, `Scheduler.complete_task()` | Completing a daily task adds a copy due tomorrow; weekly adds one due in 7 days; "once" tasks don't repeat |

### Sorting

`Scheduler.sort_tasks()` decides the order of the daily plan. Tasks are ordered by priority (high → low), then by preferred time, then by duration, so the most important work is placed first. `Scheduler.sort_by_time()` gives a chronological view instead. It uses `sorted()` with a `lambda` key of `(due_date, has no time, time)`. Times are stored zero-padded (`"8:00"` becomes `"08:00"`), so "HH:MM" strings sort correctly as text.

### Filtering

`Scheduler.filter_tasks(pet_name=None, completed=None)` returns tasks for one pet, tasks with a given completion status, or both combined (for example, Loki's unfinished tasks). Pet names are matched case-insensitively. When building the plan, `Scheduler.get_pending_tasks()` uses `Task.is_due()` to keep only unfinished tasks due today or earlier, so future recurring copies stay out of today's plan. `Scheduler.build_daily_plan()` then skips any task longer than the minutes remaining and records why in `Scheduler.skipped`.

### Conflict detection

`Scheduler.detect_conflicts()` looks at today's pending tasks that have a preferred time. Each task covers a window from its start to its start plus its duration. Tasks are sorted by start time, and each one is compared with the tasks after it; two overlap when the next one starts before the current one ends. The loop stops early once no later task can overlap. Back-to-back tasks (07:30–08:00 then 08:00) are not conflicts. Each overlap becomes a warning string labeled "same pet" or "different pets", which `main.py` prints and the app shows with `st.warning`. The scheduler does not rearrange the plan to fix conflicts; it leaves that decision to the owner.

### Recurring tasks

Each `Task` has a `frequency` ("daily", "weekly", or "once") and a `due_date`. `Scheduler.complete_task()` marks the earliest open task with that title done, then calls `Task.next_occurrence()`, which uses `timedelta(days=1)` or `timedelta(weeks=1)` to create a fresh copy with the next due date and adds it to the same pet. `timedelta` handles month and year rollovers automatically.

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->