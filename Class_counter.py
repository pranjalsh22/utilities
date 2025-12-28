import streamlit as st
import datetime
import holidays
import pandas as pd

st.set_page_config(page_title="Class Counter", layout="wide")
st.title("📚 Class Counter – B.Sc Physics (H) Sem VIII (2025–26)")
st.write("by Pranjal")

# ---------------------------
# Semester Date Inputs
# ---------------------------
default_start = datetime.date(2025, 12, 1)
default_end   = datetime.date(2026, 3, 21)

start_date = st.date_input("Semester Start Date", default_start)
end_date   = st.date_input("Semester End Date", default_end)

# ---------------------------
# Weekly Timetable (Editable Defaults)
# ---------------------------
st.header("🗓 Weekly Timetable (edit if required)")

default_schedule = {
    "Monday": [
        "Optical Fiber and Communication",
        "Digital Electronics and Microprocessors",
        "Advanced Materials Physics Lab"
    ],
    "Tuesday": [
        "Digital Electronics and Microprocessors",
        "Astronomical Techniques",
        "Renewable Energy Economics",
        "Astronomical Techniques Lab"
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
        "Astronomical Techniques Lab",
        "Space and Planetary Science",
        "Optical Fiber and Communication",
        "Advanced Materials Physics Lab"
    ]
}

schedule = {}
all_subjects = set()

for day, subjects in default_schedule.items():
    st.subheader(day)
    schedule[day] = []
    for i, subj in enumerate(subjects):
        val = st.text_input(f"{day} – Class {i+1}", subj, key=f"{day}_{i}")
        if val.strip():
            schedule[day].append(val)
            base = val.replace(" Lab", "").strip()
            all_subjects.add(base)

# ---------------------------
# Holidays (India + Winter Break)
# ---------------------------
holiday_list = holidays.India(years=range(start_date.year, end_date.year + 1))
auto_holidays = {d: name for d, name in holiday_list.items() if start_date <= d <= end_date}

winter_start = datetime.date(2025, 12, 25)
winter_end   = datetime.date(2026, 1, 5)

cur = winter_start
while cur <= winter_end:
    auto_holidays[cur] = "Winter Break"
    cur += datetime.timedelta(days=1)

if "holidays" not in st.session_state:
    st.session_state.holidays = dict(auto_holidays)

st.header("🏖 Manage Holidays")

if st.session_state.holidays:
    df = pd.DataFrame(
        [{"Date": d, "Holiday": n} for d,n in sorted(st.session_state.holidays.items())]
    )
    st.table(df)

col1, col2 = st.columns(2)

with col1:
    new_date = st.date_input("➕ Add custom holiday", default_start)
    new_name = st.text_input("Holiday name", "Custom Holiday")
    if st.button("Add Holiday"):
        st.session_state.holidays[new_date] = new_name

with col2:
    if st.session_state.holidays:
        remove_date = st.selectbox("Remove holiday", list(st.session_state.holidays.keys()))
        if st.button("Remove Selected Holiday"):
            st.session_state.holidays.pop(remove_date, None)

# ---------------------------
# Count Classes (Labs = 2 hours)
# ---------------------------
counts = {s: 0 for s in all_subjects}

d = start_date
while d <= end_date:
    if d.weekday() < 5 and d not in st.session_state.holidays:
        weekday = d.strftime("%A")
        for entry in schedule.get(weekday, []):
            base = entry.replace(" Lab", "").strip()
            if "Lab" in entry:
                counts[base] += 2
            else:
                counts[base] += 1
    d += datetime.timedelta(days=1)

# ---------------------------
# Final Summary
# ---------------------------
st.header("📊 Total Effective Classes in Semester")

summary = pd.DataFrame([
    {"Subject": s, "Total Classes (1hr eq.)": c}
    for s,c in sorted(counts.items(), key=lambda x: -x[1])
])

st.table(summary)
