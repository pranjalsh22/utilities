import streamlit as st
import datetime
import holidays
import pandas as pd
import math

# ---------------------------
# Fixed Semester Dates
# ---------------------------
st.title("Class Counter")
st.write("by pranjal")

START_FIXED = datetime.date(2025, 12, 1)
END_FIXED = datetime.date(2026, 3, 20)

today = datetime.date.today()

start_date = st.date_input("Start Date", START_FIXED)
end_date = st.date_input("End Date", END_FIXED)

# ---------------------------
# Holidays (India + Winter Break)
# ---------------------------
holiday_list = holidays.India(years=range(start_date.year, end_date.year + 1))
auto_holidays = {d: name for d, name in holiday_list.items() if start_date <= d <= end_date}

# Winter Break: 25 Dec 2025 – 4 Jan 2026
d = datetime.date(2025, 12, 25)
while d <= datetime.date(2026, 1, 4):
    auto_holidays[d] = "Winter Break"
    d += datetime.timedelta(days=1)

auto_holidays[datetime.date(2026, 1, 15)] = "Makarsakranti"
auto_holidays[datetime.date(2026, 3, 4)] = "Holi"

if "holidays" not in st.session_state:
    st.session_state.holidays = dict(auto_holidays)

holiday_df = pd.DataFrame([
    {"Date": d, "Day": d.strftime("%A"), "Holiday": n}
    for d, n in sorted(st.session_state.holidays.items())
])

# ---------------------------
# Weekly Timetable
# ---------------------------
schedule = {
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

all_subjects = set()
for subs in schedule.values():
    all_subjects.update(subs)

max_len = max(len(v) for v in schedule.values())
weekly_df = pd.DataFrame({k: v + [""]*(max_len-len(v)) for k,v in schedule.items()})

# ---------------------------
# Weekly Count
# ---------------------------
weekly_count = {s: 0 for s in all_subjects}
for subs in schedule.values():
    for s in subs:
        weekly_count[s] += 1

# ---------------------------
# Default Extra Classes (EDIT THESE)
# ---------------------------
DEFAULT_EXTRA_CLASSES = {
    "Optical Fiber and Communication": 0,
    "Digital Electronics and Microprocessors": 0,
    "Advanced Materials Physics": 0,
    "Astronomical Techniques": 5,
    "Renewable Energy Economics": 3,
    "Space and Planetary Science": 2,
}

if "extra_taken" not in st.session_state:
    st.session_state.extra_taken = DEFAULT_EXTRA_CLASSES.copy()

# ---------------------------
# Sidebar: Extra Classes Input
# ---------------------------
st.sidebar.header("Extra Classes Already Taken")

extra_taken = {}
for s in sorted(all_subjects):
    extra_taken[s] = st.sidebar.number_input(
        f"{s}",
        min_value=0,
        step=1,
        value=st.session_state.extra_taken.get(s, 0),
        key=f"extra_{s}"
    )
    st.session_state.extra_taken[s] = extra_taken[s]

# ---------------------------
# Count timetable-based classes
# ---------------------------
# Till today
till_today = {s: 0 for s in all_subjects}

d = start_date
while d <= end_date and d <= today:
    if d not in st.session_state.holidays:
        wd = d.strftime("%A")
        if wd in schedule:
            for s in schedule[wd]:
                till_today[s] += 1
    d += datetime.timedelta(days=1)

# Full semester
full_semester = {s: 0 for s in all_subjects}

d = start_date
while d <= end_date:
    if d not in st.session_state.holidays:
        wd = d.strftime("%A")
        if wd in schedule:
            for s in schedule[wd]:
                full_semester[s] += 1
    d += datetime.timedelta(days=1)

# ---------------------------
# Apply your rules
# ---------------------------
# Classes should have been completed till today = timetable till today + extra taken
should_have_completed = {s: till_today[s] + extra_taken[s] for s in all_subjects}

# Total classes in semester = timetable full semester + extra taken
total_classes = {s: full_semester[s] + extra_taken[s] for s in all_subjects}

# ---------------------------
# Final Summary
# ---------------------------
rows = []
for s in sorted(all_subjects):
    total_sem = total_classes[s]

    required_total = weekly_count[s] * 15
    extra_needed = required_total - total_sem

    need_90 = total_sem- math.ceil(0.90 * total_sem)
    need_85 = total_sem- math.ceil(0.85 * total_sem)
    need_80 = total_sem- math.ceil(0.80 * total_sem)

    rows.append({
        "Subject": s,
        "Classes Should Have Completed Till Today": should_have_completed[s],
        "Total Classes In Semester": total_sem,
        "Extra Classes Required": extra_needed,
        "Classes Needed for 90%": need_90,
        "Classes Needed for 85%": need_85,
        "Classes Needed for 80%": need_80,
    })

st.subheader("Class Summary")
st.table(pd.DataFrame(rows))

st.subheader("List of Holidays")
st.table(holiday_df)

st.subheader("Weekly Timetable")
st.table(weekly_df)
