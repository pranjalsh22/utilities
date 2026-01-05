import streamlit as st
import datetime
import holidays
import pandas as pd

# ---------------------------
# Fixed Dates
# ---------------------------
st.title("Class Counter")
st.write("by pranjal")

START_FIXED = datetime.date(2025, 12, 1)
END_FIXED = datetime.date(2026, 3, 21)

today = datetime.date.today()

start_date = st.date_input("Start Date", START_FIXED, disabled=True)
end_date = st.date_input("End Date", END_FIXED, disabled=True)

# ---------------------------
# Holidays (India + Extra Block)
# ---------------------------
holiday_list = holidays.India(years=range(start_date.year, end_date.year + 1))
auto_holidays = {d: name for d, name in holiday_list.items() if start_date <= d <= end_date}

# Add extra holidays: 25 Dec 2025 – 4 Jan 2026
extra_start = datetime.date(2025, 12, 25)
extra_end = datetime.date(2026, 1, 4)
current = extra_start
while current <= extra_end:
    auto_holidays[current] = "Winter Break"
    current += datetime.timedelta(days=1)

if "holidays" not in st.session_state:
    st.session_state.holidays = dict(auto_holidays)

st.header("Manage Holidays")

if st.session_state.holidays:
    holiday_df = pd.DataFrame(
        [{"Date": d, "Holiday": name} for d, name in sorted(st.session_state.holidays.items())]
    )
    st.table(holiday_df)

# ---------------------------
# Weekly Timetable (Your Data)
# ---------------------------
default_schedule = {
    "Monday": [
        "Optical Fiber and Communication",
        "Digital Electronics and Microprocessors",
        "Advanced Materials Physics",
        "Advanced Materials Physics"
    ],
    "Tuesday": [
        "Digital Electronics and Microprocessors",
        "Astronomical Techniques",
        "Renewable Energy Economics",
        "Astronomical Techniques",
        "Astronomical Techniques"
    ],
    "Wednesday": [
        "Space and Planetary Science",
        "Digital Electronics and Microprocessors",
        "Renewable Energy Economics",
        "Optical Fiber and Communication"
    ],
    "Thursday": [
        "Space and Planetary Science",
        "Astronomical Techniques"
    ],
    "Friday": [
        "Astronomical Techniques",
        "Space and Planetary Science",
        "Optical Fiber and Communication",
        "Advanced Materials Physics",
        "Advanced Materials Physics"
    ]
}

schedule = default_schedule
all_subjects = set()
for subs in schedule.values():
    all_subjects.update(subs)

# ---------------------------
# Weekly Table Display
# ---------------------------
st.subheader("Weekly Timetable")
max_len = max(len(v) for v in schedule.values())
weekly_df = pd.DataFrame({k: v + [""]*(max_len-len(v)) for k,v in schedule.items()})
st.table(weekly_df)

# ---------------------------
# Completed Classes Input
# ---------------------------
st.subheader("Enter Classes Already Completed")
completed_classes = {}
for subj in sorted(all_subjects):
    completed_classes[subj] = st.number_input(subj, min_value=0, value=0)

# ---------------------------
# Count Classes
# ---------------------------
total_classes = {s:0 for s in all_subjects}
should_have_completed = {s:0 for s in all_subjects}

d = start_date
while d <= end_date:
    if d not in st.session_state.holidays:
        wd = d.strftime("%A")
        if wd in schedule:
            for s in schedule[wd]:
                total_classes[s] += 1
                if d <= today:
                    should_have_completed[s] += 1
    d += datetime.timedelta(days=1)

# ---------------------------
# Final Summary
# ---------------------------
st.subheader("Class Summary")

rows = []
for s in sorted(all_subjects):
    rows.append({
        "Subject": s,
        "Already Completed": completed_classes[s],
        "Should Have Completed By Today": should_have_completed[s],
        "Total Classes In Semester": total_classes[s]
    })

st.table(pd.DataFrame(rows))
