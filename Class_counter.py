import streamlit as st
import datetime
import holidays
import pandas as pd

# ---------------------------
# Default dates
# ---------------------------
st.title("class counter")
st.write("by pranjal")
today = datetime.date.today()
start_date = st.date_input("📅 Start Date", today)
end_date = st.date_input("📅 End Date", today + datetime.timedelta(weeks=15))

# ---------------------------
# Holidays (India)
# ---------------------------
holiday_list = holidays.India(years=range(start_date.year, end_date.year + 1))
auto_holidays = {d: name for d, name in holiday_list.items() if start_date <= d <= end_date}

# Session state to store user-managed holidays
if "holidays" not in st.session_state:
    st.session_state.holidays = dict(auto_holidays)

st.header("🎉 Manage Holidays")

# Show current holidays
if st.session_state.holidays:
    st.write("Holidays being considered:")
    holiday_df = pd.DataFrame(
        [{"Date": d, "Holiday": name} for d, name in sorted(st.session_state.holidays.items())]
    )
    st.table(holiday_df)
else:
    st.info("No holidays selected in this range.")

# Add a holiday
col1, col2 = st.columns(2)
with col1:
    new_holiday_date = st.date_input("➕ Add custom holiday", today, key="new_holiday")
    new_holiday_name = st.text_input("Holiday name", value="Custom Holiday")
    if st.button("Add Holiday"):
        st.session_state.holidays[new_holiday_date] = new_holiday_name

# Remove a holiday
with col2:
    if st.session_state.holidays:
        remove_date = st.selectbox("🗑️ Remove holiday", list(st.session_state.holidays.keys()))
        if st.button("Remove Selected Holiday"):
            st.session_state.holidays.pop(remove_date, None)

# ---------------------------
# Default weekly subjects
# ---------------------------
default_schedule = {
    "Monday": ["MATH213", "PHYS602", "PHYS616", "PHYS605"],
    "Tuesday": ["MATH213", "PHYS605", "MATH121"],
    "Wednesday": ["PHYS616", "PHYS605", "MATH213"],
    "Thursday": ["MATH213", "MATH121", "PHYS602"],
    "Friday": ["MATH121", "PHYS602", "MATH121"],
}

st.header("📚 Weekly Schedule (Editable)")

schedule = {}
all_subjects = set()

for day, subjects in default_schedule.items():
    num_subjects = st.number_input(
        f"Number of subjects on {day}", min_value=0, max_value=10, value=len(subjects), key=f"{day}_num"
    )
    schedule[day] = []
    for i in range(num_subjects):
        subj = st.text_input(
            f"{day} - Subject {i+1}", value=subjects[i] if i < len(subjects) else "", key=f"{day}_{i}"
        )
        if subj.strip():
            schedule[day].append(subj)
            all_subjects.add(subj)

# ---------------------------
# Display Weekly Timetable
# ---------------------------
st.subheader("🗓️ Weekly Timetable")
max_len = max(len(subs) for subs in schedule.values())
table_data = {day: (subs + [""] * (max_len - len(subs))) for day, subs in schedule.items()}
weekly_df = pd.DataFrame(table_data)
st.table(weekly_df)

# ---------------------------
# Input: Already completed classes
# ---------------------------
st.subheader("✅ Enter Classes Already Completed")
completed_classes = {}
for subj in sorted(all_subjects):
    completed_classes[subj] = st.number_input(f"{subj}", min_value=0, value=0, key=f"completed_{subj}")

# ---------------------------
# Count future classes (excluding holidays)
# ---------------------------
future_classes = {subj: 0 for subj in all_subjects}

current_date = start_date
while current_date <= end_date:
    if current_date not in st.session_state.holidays:  # skip holidays
        weekday = current_date.strftime("%A")
        if weekday in schedule:
            for subj in schedule[weekday]:
                future_classes[subj] += 1
    current_date += datetime.timedelta(days=1)

# ---------------------------
# Final Summary Table
# ---------------------------
st.subheader("📊 Class Summary")

results = []
for subj in sorted(all_subjects):
    completed = completed_classes.get(subj, 0)
    expected = future_classes.get(subj, 0)
    total = completed + expected
    results.append({
        "Subject": subj,
        "Already Completed": completed,
        "Expected in Date Range": expected,
        "Net Classes (Total)": total
    })

summary_df = pd.DataFrame(results)
st.table(summary_df)
