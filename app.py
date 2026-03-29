import os
import streamlit as st
from pawpal_system import Owner, Pet, Task, PRIORITY_MAP
from scheduler import Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

DATA_FILE = "data.json"

# --- Session state init: load from file on first run ---
if "owner" not in st.session_state:
    if os.path.exists(DATA_FILE):
        try:
            st.session_state.owner = Owner.load_from_json(DATA_FILE)
        except Exception:
            st.session_state.owner = None
    else:
        st.session_state.owner = None


def save_state():
    if st.session_state.owner:
        st.session_state.owner.save_to_json(DATA_FILE)


def current_pet():
    """Always return the live pet from the owner's list, never a stale reference."""
    if st.session_state.owner and st.session_state.owner.pets:
        return st.session_state.owner.pets[0]
    return None


# --- Owner & Pet Info ---
st.subheader("Owner & Pet Info")

# Pre-populate form from loaded data so re-saving doesn't wipe tasks
_owner = st.session_state.owner
_pet = current_pet()
_default_owner = _owner.name if _owner else "Jordan"
_default_minutes = _owner.available_minutes if _owner else 90
_default_pet = _pet.name if _pet else "Mochi"
_default_species_idx = ["dog", "cat", "other"].index(_pet.species) if _pet and _pet.species in ["dog", "cat", "other"] else 0
_default_prefs = _owner.preferences if _owner else []

col1, col2 = st.columns(2)
with col1:
    owner_name = st.text_input("Owner name", value=_default_owner)
    available_minutes = st.number_input("Available time (minutes)", min_value=10, max_value=480, value=_default_minutes)
with col2:
    pet_name = st.text_input("Pet name", value=_default_pet)
    species = st.selectbox("Species", ["dog", "cat", "other"], index=_default_species_idx)

preferences = st.multiselect(
    "Preferred times of day (tasks matching these appear first)",
    ["morning", "afternoon", "evening"],
    default=_default_prefs,
)

if st.button("Save Owner & Pet"):
    existing_tasks = _pet.tasks if _pet else []
    pet = Pet(name=pet_name, species=species, tasks=list(existing_tasks))
    owner = Owner(name=owner_name, available_minutes=int(available_minutes), preferences=preferences)
    owner.add_pet(pet)
    st.session_state.owner = owner
    save_state()
    st.success(f"Saved {owner_name} with pet {pet_name} ({species}), {available_minutes} min available.")

st.divider()

# --- Add Tasks ---
st.subheader("Add a Task")

_pet = current_pet()
if _pet is None:
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
        priority_label = st.selectbox("Priority", ["High", "Medium", "Low"], index=1)
        task_time = st.text_input("Scheduled time (HH:MM, optional)", value="", placeholder="e.g. 08:30")
        recurrence = st.selectbox("Recurrence", ["none", "daily", "weekly"])

    if st.button("Add Task"):
        task = Task(
            name=task_title,
            duration_minutes=int(duration),
            priority=PRIORITY_MAP[priority_label],
            preferred_time=preferred_time if preferred_time != "any" else None,
            time=task_time.strip() if task_time.strip() else None,
            is_required=is_required,
            recurrence=recurrence if recurrence != "none" else None,
        )
        current_pet().add_task(task)
        save_state()
        st.success(f"Added: **{task.name}** — {task.priority_label}, {task.duration_minutes} min")

    _pet = current_pet()
    if _pet.tasks:
        scheduler = Scheduler(owner=st.session_state.owner, pet=_pet)
        priority_sorted = scheduler._sort_by_priority(_pet.tasks)
        sorted_tasks = scheduler.sort_by_time(priority_sorted)

        conflicts = scheduler.detect_conflicts(_pet.tasks)
        for warning in conflicts:
            st.warning(warning)

        st.markdown("**Current tasks (by priority, then time):**")
        rows = [
            {
                "Priority": t.priority_label,
                "Task": ("✅ " if t.completed else "") + t.name,
                "Time": t.time or "—",
                "Duration (min)": t.duration_minutes,
                "Preferred Time": t.preferred_time or "any",
                "Required": "✓" if t.is_required else "",
                "Recurrence": t.recurrence or "none",
            }
            for t in sorted_tasks
        ]
        st.table(rows)
    else:
        st.info("No tasks yet. Add one above.")

st.divider()

# --- Generate Schedule ---
st.subheader("Generate Schedule")

if st.button("Generate schedule"):
    _pet = current_pet()
    if st.session_state.owner is None or _pet is None:
        st.warning("Please save your owner and pet info first.")
    elif not _pet.tasks:
        st.warning("Add at least one task before generating a schedule.")
    else:
        scheduler = Scheduler(owner=st.session_state.owner, pet=_pet)
        plan = scheduler.schedule()

        conflicts = scheduler.detect_conflicts(_pet.tasks)
        for warning in conflicts:
            st.warning(warning)

        st.markdown("### Today's Schedule")
        if plan.scheduled_tasks:
            rows = [
                {
                    "Priority": t.priority_label,
                    "Task": t.name,
                    "Time": t.time or "—",
                    "Duration (min)": t.duration_minutes,
                    "Required": "✓" if t.is_required else "",
                    "Recurrence": t.recurrence or "—",
                }
                for t in plan.scheduled_tasks
            ]
            st.table(rows)
            st.success(f"✅ Scheduled {len(plan.scheduled_tasks)} task(s) — {plan.total_minutes} of {st.session_state.owner.available_minutes} min used.")
        else:
            st.warning("No tasks could be scheduled within the available time.")

        if plan.skipped_tasks:
            st.markdown("**⏭️ Skipped (not enough time):**")
            skipped_rows = [
                {
                    "Priority": t.priority_label,
                    "Task": t.name,
                    "Duration (min)": t.duration_minutes,
                }
                for t in plan.skipped_tasks
            ]
            st.table(skipped_rows)

        st.info(plan.reasoning)
