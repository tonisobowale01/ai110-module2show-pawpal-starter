from datetime import datetime, timedelta

import streamlit as st
from pawpal_system import Pet, Task, Owner, Scheduler, DAY_START

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Jordan")
available_minutes = st.number_input(
    "Available minutes today", min_value=1, max_value=1440, value=60
)

if "pets" not in st.session_state:
    st.session_state.pets = []

if "owner" not in st.session_state:
    st.session_state.owner = Owner(
        owner_name, available_minutes=int(available_minutes), pets=st.session_state.pets
    )
else:
    st.session_state.owner.update(name=owner_name, available_minutes=int(available_minutes))
    st.session_state.owner.pets = st.session_state.pets

if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler(st.session_state.owner)

scheduler = st.session_state.scheduler

st.markdown("### Pets")
st.caption("Add every pet the owner is caring for.")

pet_col1, pet_col2 = st.columns(2)
with pet_col1:
    new_pet_name = st.text_input("Pet name", value="", key="new_pet_name")
with pet_col2:
    new_species = st.selectbox("Species", ["dog", "cat", "other"], key="new_pet_species")

if st.button("Add pet"):
    if new_pet_name.strip():
        st.session_state.pets.append(Pet(new_pet_name.strip(), new_species))
    else:
        st.warning("Enter a pet name before adding.")

if st.session_state.pets:
    st.table(
        [{"Name": pet.name, "Species": pet.species} for pet in st.session_state.pets]
    )
else:
    st.info("No pets yet. Add one above.")

st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")

if not st.session_state.pets:
    st.info("Add a pet before adding tasks.")
else:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
    with col4:
        pet_by_name = {pet.name: pet for pet in st.session_state.pets}
        task_pet_name = st.selectbox("For pet", list(pet_by_name.keys()))

    if st.button("Add task"):
        task_pet = pet_by_name[task_pet_name]
        task = Task(task_title, int(duration), priority, pet=task_pet)
        task_pet.add_task(task)
        scheduler.add_task(task)

PRIORITY_BADGE = {"high": "🔴 High", "medium": "🟡 Medium", "low": "🟢 Low"}

if scheduler.tasks:
    st.write("Current tasks:")

    filter_col1, filter_col2, sort_col = st.columns(3)
    with filter_col1:
        completed_filter = st.selectbox(
            "Filter by status", ["All", "Completed", "Not completed"]
        )
    with filter_col2:
        pet_names = sorted({task.pet.name for task in scheduler.tasks})
        pet_filter = st.selectbox("Filter by pet", ["All pets"] + pet_names)
    with sort_col:
        sort_choice = st.selectbox("Sort by", ["Duration (longest first)", "Due date"])

    completed_arg = {"All": None, "Completed": True, "Not completed": False}[completed_filter]
    pet_arg = None if pet_filter == "All pets" else pet_filter
    filtered = scheduler.filter_tasks(completed=completed_arg, pet_name=pet_arg)

    if sort_choice == "Duration (longest first)":
        display_tasks = scheduler.sort_by_time(filtered, descending=True)
    else:
        display_tasks = scheduler.sort_by_due_date(filtered)

    if display_tasks:
        st.dataframe(
            [
                {
                    "Title": task.name,
                    "Priority": PRIORITY_BADGE.get(task.priority, task.priority),
                    "Duration (min)": task.duration,
                    "Pet": task.pet.name,
                    "Due": task.due_date.strftime("%Y-%m-%d %H:%M") if task.due_date else "—",
                    "Completed": "✅" if task.completed else "⬜",
                }
                for task in display_tasks
            ],
            width="stretch",
            hide_index=True,
        )
    else:
        st.info("No tasks match the selected filters.")

    conflicts = scheduler.detect_conflicts(filtered)
    if conflicts:
        for warning in conflicts:
            st.warning(warning)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("Generates a daily plan using Scheduler.generate_plan().")

if st.button("Generate schedule"):
    scheduler.generate_plan()

    metric_col1, metric_col2, metric_col3 = st.columns(3)
    metric_col1.metric("Scheduled", len(scheduler.plan))
    metric_col2.metric("Skipped", len(scheduler.skipped))
    used_minutes = sum(task.duration for task in scheduler.plan)
    metric_col3.metric(
        "Time used", f"{used_minutes}/{st.session_state.owner.available_minutes} min"
    )

    if scheduler.conflicts:
        for warning in scheduler.conflicts:
            st.warning(warning)

    if scheduler.plan:
        current_time = datetime.strptime(DAY_START, "%H:%M")
        rows = []
        for task in scheduler.plan:
            rows.append(
                {
                    "Time": current_time.strftime("%H:%M"),
                    "Task": task.name,
                    "Pet": task.pet.name,
                    "Duration (min)": task.duration,
                    "Priority": PRIORITY_BADGE.get(task.priority, task.priority),
                }
            )
            current_time += timedelta(minutes=task.duration)
        st.dataframe(rows, width="stretch", hide_index=True)
    else:
        st.info("No tasks scheduled.")

    if scheduler.skipped:
        with st.expander(f"Skipped tasks ({len(scheduler.skipped)})"):
            st.dataframe(
                [
                    {
                        "Task": task.name,
                        "Pet": task.pet.name,
                        "Duration (min)": task.duration,
                        "Priority": PRIORITY_BADGE.get(task.priority, task.priority),
                    }
                    for task in scheduler.skipped
                ],
                width="stretch",
                hide_index=True,
            )

    with st.expander("Why this plan", expanded=True):
        st.text(scheduler.explain_plan())
