import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("Plan your pets' care for the day based on time and priority.")

# --- App memory: create the Owner once, then reuse it on every rerun ---
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", available_minutes=60)

owner = st.session_state.owner

# --- Owner info ---
st.subheader("Owner")
col1, col2, col3 = st.columns(3)
with col1:
    owner.name = st.text_input("Owner name", value=owner.name)
with col2:
    owner.available_minutes = int(st.number_input(
        "Minutes available today", min_value=0, max_value=1440,
        value=owner.available_minutes, step=5,
    ))
with col3:
    start = st.time_input("Day starts at", value=None, step=900)
    if start is not None:
        owner.day_start = start.strftime("%H:%M")

st.divider()

# --- Add a pet: the form hands its data to Owner.add_pet() ---
st.subheader("Add a Pet")
with st.form("add_pet_form", clear_on_submit=True):
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

# --- Add a task: the form hands its data to Pet.add_task() ---
st.subheader("Add a Task")
if not owner.pets:
    st.info("Add a pet first, then you can give it tasks.")
else:
    with st.form("add_task_form", clear_on_submit=True):
        pet_choice = st.selectbox("For which pet?", [pet.name for pet in owner.pets])
        col1, col2, col3 = st.columns(3)
        with col1:
            task_title = st.text_input("Task title", placeholder="Morning walk")
        with col2:
            duration = st.number_input("Duration (minutes)", min_value=1,
                                       max_value=240, value=20)
        with col3:
            priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        col1, col2 = st.columns(2)
        with col1:
            preferred = st.time_input("Preferred time (optional)", value=None, step=900)
        with col2:
            frequency = st.selectbox("Frequency", ["daily", "weekly", "once"])

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
                    st.success(f"Added '{task.title}' for {pet_choice}.")
                except ValueError as error:
                    st.error(str(error))

# --- Current pets and tasks: read straight from the Owner object ---
st.subheader("Your Pets")
if not owner.pets:
    st.write("No pets yet.")
for pet in owner.pets:
    st.markdown(f"**{pet.name}** ({pet.species})")
    if pet.tasks:
        st.table([
            {
                "Task": task.title,
                "Minutes": task.duration_minutes,
                "Priority": task.priority,
                "Preferred time": task.time or "-",
                "Frequency": task.frequency,
                "Done": "✅" if task.completed else "",
            }
            for task in pet.tasks
        ])
    else:
        st.caption("No tasks yet.")

st.divider()

# --- Build the schedule: the button hands the Owner to the Scheduler ---
st.subheader("Today's Schedule")
if st.button("Generate schedule", type="primary"):
    scheduler = Scheduler(owner)
    plan = scheduler.build_daily_plan()

    if not plan and not scheduler.skipped:
        st.info("No pending tasks to schedule. Add some tasks above.")
    else:
        possessive = f"{owner.name}'" if owner.name.lower().endswith("s") else f"{owner.name}'s"
        st.markdown(f"#### Plan for {possessive} pets")
        if plan:
            st.table([
                {
                    "Time": f"{entry.start_time} - {entry.end_time}",
                    "Pet": entry.pet.name,
                    "Task": entry.task.title,
                    "Why": entry.reason,
                }
                for entry in plan
            ])
        used = sum(entry.task.duration_minutes for entry in plan)
        st.caption(f"Time used: {used} of {owner.available_minutes} minutes")

        for pet, task, reason in scheduler.skipped:
            st.warning(f"Skipped {pet.name}: {task.title} ({reason})")
