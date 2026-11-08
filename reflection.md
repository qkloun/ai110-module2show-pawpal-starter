# PawPal+ Project Reflection

## 1. System Design

**Core actions**
Three core actions that the user should be able to perform:
- Add a pet
- See current tasks/schedule for the day
- Pet specific care information

**a. Initial design**

My initial UML design had four classes: `Owner`, `Pet`, `Task`, and `Scheduler`. An Owner has one or more Pets, each Pet has its own list of Tasks, and the Scheduler works from the Owner to build a daily plan. I kept data and logic separate: the first three classes mostly hold information, while the Scheduler holds the planning logic, which makes it easier to test.

- **Task** represents a single care activity, like a walk or feeding. It stores the title, duration in minutes, priority, and whether it's completed, and it can mark itself complete and convert its priority into a number for sorting.
- **Pet** stores the pet's name and species along with its care tasks, and is responsible for adding tasks and returning the ones still pending.
- **Owner** stores the owner's name, the minutes they have for pet care today, what time their day starts, and their pets. It can add and look up pets and gathers every pet's tasks into one list for the Scheduler.
- **Scheduler** takes an Owner, sorts tasks by priority, fits them into the available time starting at `day_start`, and explains why each task was chosen and when it happens.

I used dataclasses for Task, Pet, and Owner because they are mainly data containers, and made Scheduler a regular class because it holds behavior and the working plan.

**b. Design changes**

Yes, the design changed in several ways during implementation. The biggest change was adding a `ScheduledTask` dataclass. I originally planned to store the plan as tuples of (start time, task, reason), but once I needed the pet's name in each entry and an end time for display, the tuples became hard to read, so a small class with named fields was clearer. I also changed `Owner.get_all_tasks()` to return `(pet, task)` pairs instead of just tasks, because the plan, filters, and conflict warnings all need to know which pet a task belongs to. Later phases added `time`, `frequency`, and `due_date` to `Task`, plus `next_occurrence()`, `is_due()`, `sort_by_time()`, `filter_tasks()`, and `detect_conflicts()`. These were features I had deliberately left out of the first draft to keep it simple.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers four constraints: the owner's available minutes for the day, each task's priority, each task's preferred time, and whether a task is due today (unfinished and due today or earlier). I decided time and priority mattered most because the scenario is a busy owner who can't do everything, so the plan has to guarantee that the most important care happens within the time they actually have. Preferred time matters less, so it only breaks ties within the same priority, and due dates act as a filter so recurring tasks for future days don't crowd out today.

**b. Tradeoffs**

My scheduler places tasks greedily by priority, from high to low, back to back starting at the owner's day start, and skips any task that doesn't fit in the remaining time. A task's preferred time only breaks ties within the same priority, so a task the owner wants at 08:00 might land at 08:10, and overlapping preferred times produce a warning rather than a rearranged plan. I think this is reasonable for a busy pet owner because it guarantees that critical tasks like feeding and medication always make it into the day. Honoring exact times would mean handling gaps, deciding which task moves when two clash, and dealing with time slots that have already passed, which would make the logic much harder to understand and test. Flagging conflicts instead of resolving them keeps the scheduler predictable and leaves the final call to the owner, who knows their day better than the app does.

---

## 3. AI Collaboration

**a. How you used AI**

I used AI throughout the project: brainstorming classes and drafting the Mermaid UML, generating class skeletons with dataclasses, implementing the scheduling methods, debugging (for example, a `ModuleNotFoundError` when pytest couldn't find `pawpal_system.py`), writing tests, and polishing the Streamlit UI and README. The most effective features were chat for explaining concepts before I used them, like `st.session_state`, `lambda` sort keys, and `timedelta`, and multi-file edits for changes that touched several files at once, like recurring tasks, which needed updates to `pawpal_system.py`, `app.py`, `main.py`, and the tests together. The most helpful prompts were specific and referenced my own code, such as "Based on my skeletons in `pawpal_system.py`, how should the `Scheduler` retrieve all tasks from the `Owner`'s pets?", and review prompts like "How could this algorithm be simplified for better readability or performance?"

Using separate chat sessions for different phases helped me stay organized because each session had one clear goal, such as design, implementation, or testing. That kept the AI focused on the files that mattered for that phase instead of mixing old context into new work, and it made it easier for me to review one kind of change at a time.

**b. Judgment and verification**

When I asked the AI to simplify `detect_conflicts()`, it suggested a version using `itertools.combinations` with a two-sided overlap check (`a_start < b_end and b_start < a_end`). It was shorter and more "Pythonic," but the overlap condition is harder to verify at a glance than my version's logic ("the next task starts before this one ends"), it checked every pair instead of stopping early, and it dropped useful details from the warning messages. I kept my original version because it was easier to explain and my tests already proved it worked.

I also caught a design problem in the recurring-task feature. Marking a daily task complete correctly created tomorrow's copy, but without a due-date check that copy would have appeared in today's plan right away. I verified suggestions like this by running `main.py`, checking the output by hand, and adding tests (such as "tomorrow's copy is not in today's plan") so the behavior stays correct.

---

## 4. Testing and Verification

**a. What you tested**

My 22 tests cover five areas: basic behavior (completing tasks, adding tasks, rejecting invalid tasks and duplicate pet names), sorting (chronological order, unpadded hours like "8:00", untimed tasks last, and high priority first in the plan), filtering and the time budget (filtering by pet and status, skipping tasks that don't fit, empty plans, overdue tasks), recurrence (daily and weekly copies, month rollover, one-time tasks, future copies staying out of today's plan), and conflict detection (same pet, different pets, partial overlaps, back-to-back tasks, completed tasks). These tests matter because the scheduler's whole value is making correct decisions automatically. If sorting or recurrence silently broke, a pet could miss medication without the owner noticing. The tests use a fixed date so they give the same result any day they're run.

**b. Confidence**

I'm fairly confident, about 4 out of 5, that the scheduler works correctly. All tests pass, including the edge cases I thought were most likely to break. With more time, I would test tasks that run past midnight, two open tasks with the same title on one pet, an owner with zero available minutes, and the Streamlit UI itself, which I only tested by hand.

---

## 5. Reflection

**a. What went well**

I'm most satisfied with how cleanly the logic layer is separated from the interfaces. Because all the rules live in `pawpal_system.py`, both `main.py` and the Streamlit app use the exact same scheduling behavior, and I could test it thoroughly without touching the UI.

**b. What you would improve**

With another iteration, I would make the scheduler actually honor preferred times by placing tasks at their requested slots and resolving conflicts, rather than only warning about them. I would also let users edit and delete tasks in the UI and save data between sessions, since everything currently resets when the browser tab is closed.

**c. Key takeaway**

The most important thing I learned is that I have to be the lead architect when working with AI. The AI can write code quickly, but it doesn't decide what the system should be. I had to choose the classes and their responsibilities, keep the first design simple, judge whether a "cleverer" suggestion was actually better, and notice when a feature that worked on its own broke something else, like recurring tasks showing up a day early. Starting with a UML design gave me a plan to measure the AI's suggestions against, and tests gave me a way to prove its code actually did what I intended.