import streamlit as st
import pandas as pd
from datetime import date, timedelta

st.set_page_config(page_title="Class Counter", layout="centered")

st.title("📚 Class Counter App")

st.markdown("This app estimates how many classes will be completed by the end of the semester based on weekly schedule and holidays.")

# Subject setup
st.header("Step 1: Define Subjects and Weekly Schedule")

num_subjects = st.number_input("How many subjects?", min_value=1, max_value=10, value=3, step=1)
subjects = {}

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

for i in range(num_subjects):
    st.subheader(f"Subject {i+1}")
    subject_name = st.text_input(f"Enter subject name {i+1}", key=f"name_{i}")
    weekly_schedule = {}
    cols = st.columns(5)
    for j, day in enumerate(days):
        weekly_schedule[day] = cols[j].number_input(f"{day}", min_value=0, max_value=10, value=0, key=f"{subject_name}_{day}")
    completed = st.number_input(f"Number of classes already completed in {subject_name}", min_value=0, value=0, key=f"done_{subject_name}")
    subjects[subject_name] = {
        "weekly_schedule": weekly_schedule,
        "completed": completed
    }

# Date inputs
st.header("Step 2: Set Date Range")

start_date = st.date_input("Start date", value=date.today())
end_date = st.date_input("End date", value=date.today() + timedelta(weeks=15))

# Days off
st.header("Step 3: Enter Off Days (Holidays, Semester Breaks)")

off_days = st.date_input("Select holidays or breaks (no classes will be counted on these days)", [])

# Count logic
st.header("📊 Result: Total Classes by End Date")

if st.button("Calculate"):
    total_classes = {subject: 0 for subject in subjects}
    
    current_date = start_date
    while current_date <= end_date:
        if current_date in off_days:
            current_date += timedelta(days=1)
            continue
        weekday = current_date.strftime("%A")
        for subject, info in subjects.items():
            weekly_schedule = info["weekly_schedule"]
            total_classes[subject] += weekly_schedule.get(weekday, 0)
        current_date += timedelta(days=1)

    # Display results
    results = []
    for subject, info in subjects.items():
        done = info["completed"]
        total = total_classes[subject]
        remaining = max(total - done, 0)
        results.append({
            "Subject": subject,
            "Classes Completed": done,
            "Expected by End Date": total,
            "Remaining": remaining
        })

    df = pd.DataFrame(results)
    st.dataframe(df)
