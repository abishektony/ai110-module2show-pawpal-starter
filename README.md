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

## Smarter Scheduling

The scheduling logic lives in `scheduler.py`, separate from the data model in `pawpal_system.py`. This separation keeps algorithmic changes isolated from core classes.

**Chronological sorting** — `sort_by_time()` orders tasks by their `HH:MM` time attribute using a lambda key. Tasks without a time are placed at the end. String comparison on zero-padded hour strings matches chronological order, so no date parsing is needed.

**Conflict detection** — `detect_conflicts()` groups tasks by time slot and returns a warning message for any slot with more than one task. It never raises an exception — callers decide how to surface the warnings. Accepts a merged task list so cross-pet conflicts can also be checked.

**Recurrence** — `complete_task()` marks a task done and, if its `recurrence` field is `"daily"` or `"weekly"`, automatically appends a fresh copy to the pet's task list for the next occurrence. Non-recurring tasks are completed with no side effects.

**Flexible filtering** — `filter_tasks()` accepts keyword-only arguments (`completed`, `pet_name`) so callers can filter by one or both independently. Passing `None` for either skips that filter.

## Testing PawPal+

### Initialize environment
Install UV in global, a python library which is good for package management.
    
    uv init
    uv sync

### Run the tests

    uv run -m pytest tests/test_pawpal.py

### What the tests cover

The test suite has 26 tests across five areas:

| Area | What is verified |
|---|---|
| **Recurring tasks** | Daily and weekly tasks produce a new incomplete copy on completion; non-recurring and unknown recurrence values (`"monthly"`) return `None` and add no task |
| **Sorting** | `sort_by_time()` orders tasks chronologically and pushes untimed tasks to the end; `_sort_by_priority()` places lower priority numbers first and promotes required tasks within ties |
| **Conflict detection** | Same-slot tasks produce one warning listing all names; different slots and untimed tasks produce no warnings |
| **Schedule building** | Greedy packing respects available time, skips tasks that don't fit, handles zero minutes and empty task lists, and applies owner preferences before fitting |
| **Filtering** | `filter_tasks()` correctly narrows by completion status and pet name, independently or together |

### Confidence Level: ⭐⭐⭐⭐

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
