import contextlib
import io

import streamlit as st
from pawpal_system import Pet, Task, Owner, Scheduler

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
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

if "pet" not in st.session_state:
    st.session_state.pet = Pet(pet_name, species)
else:
    st.session_state.pet.update(name=pet_name, species=species)

if "owner" not in st.session_state:
    st.session_state.owner = Owner(
        owner_name, available_minutes=int(available_minutes), pets=[st.session_state.pet]
    )
else:
    st.session_state.owner.update(name=owner_name, available_minutes=int(available_minutes))

if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler(st.session_state.owner)

scheduler = st.session_state.scheduler

st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

if st.button("Add task"):
    task = Task(task_title, int(duration), priority, pet=st.session_state.pet)
    st.session_state.pet.add_task(task)
    scheduler.add_task(task)

if scheduler.tasks:
    st.write("Current tasks:")
    st.table(
        [
            {
                "title": task.name,
                "duration_minutes": task.duration,
                "priority": task.priority,
                "pet": task.pet.name,
                "completed": task.completed,
            }
            for task in scheduler.tasks
        ]
    )
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("Generates a daily plan using Scheduler.generate_plan().")

if st.button("Generate schedule"):
    scheduler.generate_plan()

    plan_output = io.StringIO()
    with contextlib.redirect_stdout(plan_output):
        scheduler.display_plan()
    st.text(plan_output.getvalue())

    st.markdown("**Why this plan:**")
    st.text(scheduler.explain_plan())
