import streamlit as st
import pandas as pd
from datetime import date, timedelta

st.set_page_config(page_title="Class Counter", layout="centered")
st.title("Class Counter by Pranjal")

# --- Step 1: Subject setup ---
st.header("Step 1: Weekly Schedule")

# Default subjects and their weekly schedules
default_schedule = {
    "MATH213": {"Monday": 1, "Tuesday": 1, "Wednesday": 1, "Thursday": 1, "Friday": 0},
    "PHYS602": {"Monday": 1, "Tuesday": 0, "Wednesday": 0, "Thursday": 1, "Friday": 1},
    "PHYS616": {"Monday": 1, "Tuesday": 0, "Wednesday": 1, "Thursday": 0, "Friday": 0},
    "PHY605":  {"Monday": 1, "Tuesday": 1, "Wednesday": 1, "Thursday": 0, "Friday": 0},
    "MATH121": {"Monday": 0, "Tuesday": 1, "Wednesday": 0, "Thursday": 1, "Friday": 2},
}

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
subjects = {}

for i, (subj, sched) in enumerate(default_schedule.items()):
    st.subheader(f"{subj}")
    weekly_schedule = {}
    cols = st.columns(len(days))
    for j, day in enumerate(days):
        weekly_schedule[day] = cols[j].number_input(
            f"{day}", min_value=0, max_value=10, 
            value=sched.get(day, 0), key=f"{subj}_{day}"
        )
    completed = st.number_input(
        f"Number of classes already completed in {subj}",
        min_value=0, value=0, key=f"done_{subj}"
    )
    subjects[subj] = {
        "name": subj,
        "weekly_schedule": weekly_schedule,
        "completed": completed
    }

# --- Step 2: Date inputs ---
st.header("Step 2: Set Date Range")

today = date.today()
start_date = st.date_input("Start date", value=today)
end_date = st.date_input("End date", value=today + timedelta(weeks=15))

# --- Step 3: Days off ---
st.header("Step 3: Add Days Off (Holidays, Breaks)")

if "off_days" not in st.session_state:
    st.session_state.off_days = set()

new_off_day = st.date_input("📅 Pick a day off", value=today)
col1, col2 = st.columns(2)
if col1.button("➕ Add this day off"):
    st.session_state.off_days.add(new_off_day)
if col2.button("🗑️ Clear all days off"):
    st.session_state.off_days.clear()

if st.session_state.off_days:
    sorted_days = sorted(st.session_state.off_days)
    st.markdown("### 📌 Selected Days Off:")
    st.write(sorted_days)
else:
    st.info("No off days selected yet.")

# --- Step 4: Results ---
st.header("Result: Projected Class Counts by End Date")

if st.button("Calculate"):
    total_future_classes = {key: 0 for key in subjects}

    current_date = start_date
    while current_date <= end_date:
        if current_date in st.session_state.off_days:
            current_date += timedelta(days=1)
            continue
        weekday = current_date.strftime("%A")
        for key, info in subjects.items():
            total_future_classes[key] += info["weekly_schedule"].get(weekday, 0)
        current_date += timedelta(days=1)

    results = []
    for key, info in subjects.items():
        completed = info["completed"]
        expected = total_future_classes[key]
        total_by_end = completed + expected
        results.append({
            "Subject": info["name"],
            "Classes Already Completed": completed,
            "Classes Expected (From Today)": expected,
            "Total Classes by End Date": total_by_end
        })

    df = pd.DataFrame(results)
    st.dataframe(df, use_container_width=True)
