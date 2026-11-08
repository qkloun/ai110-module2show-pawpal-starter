import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

PRIORITY_LABELS = {"high": "🔴 High", "medium": "🟡 Medium", "low": "🟢 Low"}


def possessive(name: str) -> str:
    """Return "James'" or "Jordan's" depending on the last letter."""
    return f"{name}'" if name.lower().endswith("s") else f"{name}'s"


# --- App memory: create the Owner once, then reuse it on every rerun ---
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", available_minutes=60)

owner = st.session_state.owner

st.title("🐾 PawPal+")
st.caption("Plan your pets' care for the day based on your time and each task's priority.")

# --- Owner info ---
with st.container(border=True):
    st.subheader("Your day")
    col1, col2, col3 = st.columns(3)
    with col1:
        owner.name = st.text_input("Owner name", value=owner.name)
    with col2:
        owner.available_minutes = int(st.number_input(
            "Minutes available", min_value=0, max_value=1440,
            value=owner.available_minutes, step=5,
        ))
    with col3:
        start = st.time_input("Day starts at", value=None, step=900)
        if start is not None:
            owner.day_start = start.strftime("%H:%M")

pets_tab, tasks_tab, schedule_tab = st.tabs(["Pets", "Tasks", "Today's schedule"])

# =====================================================================
# Pets tab: Owner.add_pet()
# =====================================================================
with pets_tab:
    with st.form("add_pet_form", clear_on_submit=True):
        st.markdown("**Add a pet**")
        col1, col2 = st.columns(2)
        with col1:
            pet_name = st.text_input("Pet name")
        with col2:
            species = st.selectbox("Species", ["dog", "cat", "other"])
        if st.form_submit_button("Add pet"):
            if not pet_name.strip():
                st.error("Please enter a pet name.")
            else:
                try:
                    owner.add_pet(Pet(name=pet_name.strip(), species=species))
                    st.success(f"Added {pet_name.strip()}!")
                except ValueError as error:
                    st.error(str(error))

    if owner.pets:
        st.table([
            {
                "Pet": pet.name,
                "Species": pet.species,
                "Open tasks": len(pet.get_pending_tasks()),
            }
            for pet in owner.pets
        ])
    else:
        st.info("No pets yet. Add your first pet above.")

# =====================================================================
# Tasks tab: Pet.add_task(), Scheduler.complete_task(),
#            Scheduler.filter_tasks() + Scheduler.sort_by_time()
# =====================================================================
with tasks_tab:
    # Messages saved before a rerun (so every tab reflects the change right away)
    if "flash" in st.session_state:
        st.success(st.session_state.pop("flash"))

    if not owner.pets:
        st.info("Add a pet first, then you can give it tasks.")
    else:
        with st.form("add_task_form", clear_on_submit=True):
            st.markdown("**Add a task**")
            pet_choice = st.selectbox("For which pet?", [pet.name for pet in owner.pets])
            col1, col2, col3 = st.columns(3)
            with col1:
                task_title = st.text_input("Task title", placeholder="Morning walk")
            with col2:
                duration = st.number_input("Duration (min)", min_value=1,
                                           max_value=240, value=20)
            with col3:
                priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
            col1, col2 = st.columns(2)
            with col1:
                preferred = st.time_input("Preferred time (optional)",
                                          value=None, step=900)
            with col2:
                frequency = st.selectbox("Repeats", ["daily", "weekly", "once"])

            if st.form_submit_button("Add task"):
                if not task_title.strip():
                    st.error("Please enter a task title.")
                else:
                    try:
                        task = Task(
                            title=task_title.strip(),
                            duration_minutes=int(duration),
                            priority=priority,
                            time=preferred.strftime("%H:%M") if preferred else None,
                            frequency=frequency,
                        )
                        owner.get_pet(pet_choice).add_task(task)
                        st.session_state.flash = f"Added '{task.title}' for {pet_choice}."
                        st.rerun()
                    except ValueError as error:
                        st.error(str(error))

        open_tasks = [(pet, task) for pet, task in owner.get_all_tasks()
                      if not task.completed]
        if open_tasks:
            with st.form("complete_task_form"):
                st.markdown("**Mark a task complete**")
                choice = st.selectbox(
                    "Task",
                    range(len(open_tasks)),
                    format_func=lambda i: (
                        f"{open_tasks[i][0].name}: {open_tasks[i][1].title} "
                        f"(due {open_tasks[i][1].due_date:%a %b %d})"),
                )
                if st.form_submit_button("Mark complete"):
                    pet, task = open_tasks[choice]
                    next_task = Scheduler(owner).complete_task(pet.name, task.title)
                    if next_task:
                        st.session_state.flash = (
                            f"Nice! '{task.title}' is done. The next one is due "
                            f"{next_task.due_date:%A, %b %d}.")
                    else:
                        st.session_state.flash = (
                            f"Nice! '{task.title}' is done. It was a one-time task.")
                    st.rerun()

        st.markdown("**All tasks**")
        col1, col2 = st.columns(2)
        with col1:
            pet_filter = st.selectbox("Pet", ["All pets"] + [p.name for p in owner.pets])
        with col2:
            status_filter = st.radio("Status", ["Pending", "Completed", "All"],
                                     horizontal=True)

        scheduler = Scheduler(owner)
        filtered = scheduler.filter_tasks(
            pet_name=None if pet_filter == "All pets" else pet_filter,
            completed={"Pending": False, "Completed": True, "All": None}[status_filter],
        )
        rows = scheduler.sort_by_time(filtered)
        if rows:
            st.caption("Sorted by due date, then preferred time.")
            st.table([
                {
                    "Due": task.due_date.strftime("%a %b %d"),
                    "Time": task.time or "Any time",
                    "Pet": pet.name,
                    "Task": task.title,
                    "Minutes": task.duration_minutes,
                    "Priority": PRIORITY_LABELS[task.priority],
                    "Repeats": task.frequency,
                    "Status": "✅ Done" if task.completed else "Pending",
                }
                for pet, task in rows
            ])
        else:
            st.info("No tasks match these filters.")

# =====================================================================
# Schedule tab: Scheduler.detect_conflicts() + build_daily_plan()
# =====================================================================
with schedule_tab:
    scheduler = Scheduler(owner)
    conflicts = scheduler.detect_conflicts()
    plan = scheduler.build_daily_plan()

    if not plan and not scheduler.skipped:
        st.info("Nothing to schedule today. Add tasks in the Tasks tab.")
    else:
        st.subheader(f"Plan for {possessive(owner.name)} pets")

        used = sum(entry.task.duration_minutes for entry in plan)
        col1, col2, col3 = st.columns(3)
        col1.metric("Tasks scheduled", len(plan))
        col2.metric("Minutes used", f"{used} / {owner.available_minutes}")
        col3.metric("Skipped", len(scheduler.skipped))

        # Conflicts first: they need the owner's attention before the plan is trusted
        if conflicts:
            st.warning(
                f"**{len(conflicts)} time conflict{'s' if len(conflicts) > 1 else ''}** "
                "among your preferred times. You can't do these at once, so PawPal+ "
                "placed them back to back by priority below. To fix this, change one "
                "task's preferred time or shorten it.\n\n"
                + "\n".join(f"- {warning}" for warning in conflicts)
            )

        if plan:
            st.table([
                {
                    "Time": f"{entry.start_time} - {entry.end_time}",
                    "Pet": entry.pet.name,
                    "Task": entry.task.title,
                    "Priority": PRIORITY_LABELS[entry.task.priority],
                    "Why": entry.reason,
                }
                for entry in plan
            ])

        if scheduler.skipped:
            st.warning(
                "**Didn't fit today.** Free up more time or lower other tasks' "
                "priority to include these:\n\n"
                + "\n".join(f"- {pet.name}: {task.title} ({reason})"
                            for pet, task, reason in scheduler.skipped)
            )
        elif not conflicts:
            st.success("Everything fits, with no time conflicts. You're all set! 🐾")

        with st.expander("How PawPal+ built this plan"):
            st.markdown(
                "Tasks are placed from your day's start time, highest priority first. "
                "Within the same priority, earlier preferred times go first, then "
                "shorter tasks. Tasks that don't fit in your remaining minutes are "
                "skipped, and recurring tasks due on later days are left out."
            )
            st.code(scheduler.explain_plan(), language=None)