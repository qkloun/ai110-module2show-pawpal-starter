# 🐾 PawPal+

PawPal+ is a Streamlit app that helps a busy pet owner stay consistent with pet care. You enter your pets, their care tasks, and how much time you have today, and PawPal+ builds a daily plan that puts the most important tasks first, warns you about time clashes, explains its choices, and keeps recurring tasks coming back automatically.

## ✨ Features

- **Owner and pet profiles:** set your name, the minutes you have for pet care today, and when your day starts; add any number of pets (duplicate names are rejected).
- **Task tracking:** each task has a title, duration, priority (low/medium/high), optional preferred time, and a repeat setting (daily, weekly, or once). Invalid input like a zero-minute task or a time of "25:00" is rejected with a clear message.
- **Priority-first daily plan:** tasks are placed back to back from your start time, high priority first, then by preferred time, then shortest first, so critical care like feeding and medication always makes the cut.
- **Time-budget filtering:** tasks that don't fit in your remaining minutes are skipped and listed with the reason, instead of silently overbooking your day.
- **Sorting by time:** a chronological view of all tasks, ordered by due date and then "HH:MM" time, with untimed tasks last.
- **Filtering by pet and status:** view one pet's tasks, only pending or only completed tasks, or any combination.
- **Conflict warnings:** overlapping preferred times are detected (same pet or different pets) and shown as warnings that never crash the app; back-to-back tasks are not counted as conflicts.
- **Daily and weekly recurrence:** marking a recurring task complete automatically creates the next one, due tomorrow or in a week; future copies stay out of today's plan, and overdue tasks stay in it.
- **Plan explanations:** every scheduled task shows why it was chosen, and the app explains how the plan was built.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Run the app

```bash
streamlit run app.py
```

### Run the terminal demo

```bash
python main.py
```

## 🖥️ Sample Output

The daily plan from `python main.py`:

```
============================================================
  Today's Schedule for Yunus' pets
============================================================
  07:30 - 07:35   Mochi  Heartworm pill     [high]
  07:35 - 07:45   Mochi  Breakfast          [high]
  07:45 - 07:55   Luna   Clean litter box   [medium]
  07:55 - 08:00   Luna   Brush teeth        [medium]
  08:00 - 08:20   Luna   Play session       [medium]
------------------------------------------------------------
  Time used: 50 of 75 minutes
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

## 🏗️ System Architecture

The final class diagram is in [`diagrams/uml_final.mmd`](diagrams/uml_final.mmd) (the Phase 1 draft is in `diagrams/uml_draft.mmd`). Paste either file into [mermaid.live](https://mermaid.live/) to view it.

- `Owner` holds the day's time budget and a list of `Pet`s; each `Pet` owns its `Task`s.
- `Task` knows how to validate itself, report whether it's due, and create its next occurrence.
- `Scheduler` reads every task through `Owner.get_all_tasks()` and builds a plan made of `ScheduledTask` entries (start time, pet, task, and reason).
- All logic lives in `pawpal_system.py`; `app.py` (Streamlit) and `main.py` (terminal) only call it, so the same rules are tested once and used everywhere.

## 📸 Demo Walkthrough

### Main UI features

The app opens with a **Your day** panel for the owner's name, minutes available, and day start time. Below it are three tabs:

- **Pets:** add a pet with a name and species, and see a table of your pets with how many open tasks each has.
- **Tasks:** add a task for a chosen pet; mark any open task complete; and browse all tasks in a table you can filter by pet and by status (pending, completed, or all), sorted by due date and preferred time.
- **Today's schedule:** see summary numbers (tasks scheduled, minutes used, tasks skipped), any time-conflict warnings, the plan table with a reason for each task, a list of tasks that didn't fit, and an expandable explanation of how the plan was built.

### Example workflow

1. In **Your day**, enter "Jordan", set 75 minutes available, and a 07:30 start.
2. In **Pets**, add Mochi (dog) and Luna (cat). Both appear in the pets table.
3. In **Tasks**, add Mochi's "Morning walk" (30 min, high, 07:30, daily) and "Breakfast" (10 min, high, 09:00), then Luna's "Clean litter box" (10 min, medium, 09:00) and "Play session" (20 min, medium, 17:00).
4. Open **Today's schedule**. A yellow warning reports that Mochi's Breakfast and Luna's Clean litter box are both at 09:00, with a suggestion to change one time. The plan table lists the high-priority tasks first, each with its time slot and reason.
5. Lower the available minutes to 45. The skipped count goes up, and a warning lists the two medium-priority tasks that no longer fit and why.
6. Back in **Tasks**, mark Mochi's "Morning walk" complete. A message confirms the next walk is due tomorrow, and the task table (set to "All") shows both the completed walk and tomorrow's copy.
7. Return to **Today's schedule**. The walk is gone from today's plan, and tomorrow's copy doesn't appear.

### Key Scheduler behaviors shown

- **Priority sorting:** high-priority tasks are scheduled first, and same-priority tasks follow their preferred times (`Scheduler.sort_tasks()`).
- **Sorting and filtering:** the Tasks tab table uses `Scheduler.filter_tasks()` and `Scheduler.sort_by_time()`.
- **Conflict warnings:** `Scheduler.detect_conflicts()` results appear above the plan so the owner sees them before trusting it.
- **Time budget:** tasks that don't fit are skipped with a reason (`Scheduler.build_daily_plan()`).
- **Recurrence:** completing a daily or weekly task creates its next occurrence (`Scheduler.complete_task()`, `Task.next_occurrence()`).

### CLI output from `main.py`

`main.py` adds tasks out of order, checks sorting and filtering, detects conflicts, completes recurring tasks, and then prints today's schedule:

```
============================================================
  Sorting and filtering checks
============================================================

All tasks, unsorted (grouped by pet, in the order added):
  Sun Nov 08  18:00  Mochi  Brush coat         [low, weekly] (todo)
  Sun Nov 08  08:00  Mochi  Heartworm pill     [high, daily] (todo)
  Sun Nov 08  07:30  Mochi  Morning walk       [high, daily] (todo)
  Sun Nov 08  09:00  Mochi  Breakfast          [high, daily] (todo)
  Sun Nov 08  17:00  Luna   Play session       [medium, daily] (todo)
  Sun Nov 08  09:00  Luna   Clean litter box   [medium, daily] (todo)
  Sun Nov 08  07:45  Luna   Breakfast          [high, daily] (done)
  Sun Nov 08  09:05  Luna   Brush teeth        [medium, daily] (todo)
  Sun Nov 08  --:--  Luna   Trim claws         [low, once] (todo)
  Mon Nov 09  07:45  Luna   Breakfast          [high, daily] (todo)

Sorted by time:
  Sun Nov 08  07:30  Mochi  Morning walk       [high, daily] (todo)
  Sun Nov 08  07:45  Luna   Breakfast          [high, daily] (done)
  Sun Nov 08  08:00  Mochi  Heartworm pill     [high, daily] (todo)
  Sun Nov 08  09:00  Mochi  Breakfast          [high, daily] (todo)
  Sun Nov 08  09:00  Luna   Clean litter box   [medium, daily] (todo)
  Sun Nov 08  09:05  Luna   Brush teeth        [medium, daily] (todo)
  Sun Nov 08  17:00  Luna   Play session       [medium, daily] (todo)
  Sun Nov 08  18:00  Mochi  Brush coat         [low, weekly] (todo)
  Sun Nov 08  --:--  Luna   Trim claws         [low, once] (todo)
  Mon Nov 09  07:45  Luna   Breakfast          [high, daily] (todo)

Only Luna's tasks:
  Sun Nov 08  17:00  Luna   Play session       [medium, daily] (todo)
  Sun Nov 08  09:00  Luna   Clean litter box   [medium, daily] (todo)
  Sun Nov 08  07:45  Luna   Breakfast          [high, daily] (done)
  Sun Nov 08  09:05  Luna   Brush teeth        [medium, daily] (todo)
  Sun Nov 08  --:--  Luna   Trim claws         [low, once] (todo)
  Mon Nov 09  07:45  Luna   Breakfast          [high, daily] (todo)

Only completed tasks:
  Sun Nov 08  07:45  Luna   Breakfast          [high, daily] (done)

Mochi's pending tasks, sorted by time:
  Sun Nov 08  07:30  Mochi  Morning walk       [high, daily] (todo)
  Sun Nov 08  08:00  Mochi  Heartworm pill     [high, daily] (todo)
  Sun Nov 08  09:00  Mochi  Breakfast          [high, daily] (todo)
  Sun Nov 08  18:00  Mochi  Brush coat         [low, weekly] (todo)

============================================================
  Conflict checks
============================================================
  WARNING: Mochi's 'Breakfast' (09:00-09:10) overlaps Luna's 'Clean litter box' (09:00-09:10) [different pets]
  WARNING: Mochi's 'Breakfast' (09:00-09:10) overlaps Luna's 'Brush teeth' (09:05-09:10) [different pets]
  WARNING: Luna's 'Clean litter box' (09:00-09:10) overlaps Luna's 'Brush teeth' (09:05-09:10) [same pet]

============================================================
  Recurring task checks
============================================================
  Completed Mochi's Morning walk (daily) -> next one due Mon Nov 09
  Completed Mochi's Brush coat (weekly) -> next one due Sun Nov 15
  Completed Luna's Trim claws -> no repeat

Mochi's tasks after completing:
  Sun Nov 08  07:30  Mochi  Morning walk       [high, daily] (done)
  Sun Nov 08  08:00  Mochi  Heartworm pill     [high, daily] (todo)
  Sun Nov 08  09:00  Mochi  Breakfast          [high, daily] (todo)
  Sun Nov 08  18:00  Mochi  Brush coat         [low, weekly] (done)
  Mon Nov 09  07:30  Mochi  Morning walk       [high, daily] (todo)
  Sun Nov 15  18:00  Mochi  Brush coat         [low, weekly] (todo)

============================================================
  Today's Schedule for Jordan's pets
============================================================
  07:30 - 07:35   Mochi  Heartworm pill     [high]
  07:35 - 07:45   Mochi  Breakfast          [high]
  07:45 - 07:55   Luna   Clean litter box   [medium]
  07:55 - 08:00   Luna   Brush teeth        [medium]
  08:00 - 08:20   Luna   Play session       [medium]
------------------------------------------------------------
  Time used: 50 of 75 minutes
============================================================
```