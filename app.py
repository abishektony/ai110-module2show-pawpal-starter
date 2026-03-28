import streamlit as st
from pawpal_system import Owner, Pet, Task
from scheduler import Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# --- Session state init ---
if "owner" not in st.session_state:
    st.session_state.owner = None
if "pet" not in st.session_state:
    st.session_state.pet = None

# --- Owner & Pet Info ---
st.subheader("Owner & Pet Info")

col1, col2 = st.columns(2)
with col1:
    owner_name = st.text_input("Owner name", value="Jordan")
    available_minutes = st.number_input("Available time (minutes)", min_value=10, max_value=480, value=90)
with col2:
    pet_name = st.text_input("Pet name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Save Owner & Pet"):
    pet = Pet(name=pet_name, species=species)
    owner = Owner(name=owner_name, available_minutes=int(available_minutes))
    owner.add_pet(pet)
    st.session_state.owner = owner
    st.session_state.pet = pet
    st.success(f"Saved {owner_name} with pet {pet_name} ({species}), {available_minutes} min available.")

st.divider()

# --- Add Tasks ---
st.subheader("Add a Task")

if st.session_state.pet is None:
    st.info("Save your owner and pet info above before adding tasks.")
else:
    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
        preferred_time = st.selectbox("Preferred time", ["morning", "afternoon", "evening", "any"])
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        is_required = st.checkbox("Required?")
    with col3:
        priority = st.number_input("Priority (1 = highest)", min_value=1, max_value=5, value=2)

    if st.button("Add Task"):
        task = Task(
            name=task_title,
            duration_minutes=int(duration),
            priority=int(priority),
            preferred_time=preferred_time if preferred_time != "any" else None,
            is_required=is_required,
        )
        st.session_state.pet.add_task(task)
        st.success(f"Added task: {task}")

    if st.session_state.pet.tasks:
        st.markdown("**Current tasks:**")
        rows = [
            {
                "Task": t.name,
                "Duration (min)": t.duration_minutes,
                "Priority": t.priority,
                "Preferred Time": t.preferred_time or "any",
                "Required": t.is_required,
            }
            for t in st.session_state.pet.tasks
        ]
        st.table(rows)
    else:
        st.info("No tasks yet. Add one above.")

st.divider()

# --- Generate Schedule ---
st.subheader("Generate Schedule")

if st.button("Generate schedule"):
    if st.session_state.owner is None or st.session_state.pet is None:
        st.warning("Please save your owner and pet info first.")
    elif not st.session_state.pet.tasks:
        st.warning("Add at least one task before generating a schedule.")
    else:
        scheduler = Scheduler(owner=st.session_state.owner, pet=st.session_state.pet)
        plan = scheduler.schedule()

        st.markdown("### Today's Schedule")
        if plan.scheduled_tasks:
            for task in plan.scheduled_tasks:
                st.markdown(f"- {task}")
            st.markdown(f"**Total time:** {plan.total_minutes} min")
        else:
            st.warning("No tasks could be scheduled within the available time.")

        if plan.skipped_tasks:
            st.markdown("**Skipped (not enough time):**")
            for task in plan.skipped_tasks:
                st.markdown(f"- {task}")

        st.info(plan.reasoning)
