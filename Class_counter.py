import streamlit as st
import datetime
import pandas as pd

st.set_page_config(page_title="Class Counter", layout="wide")
st.title("📚 Class Counter – B.Sc Physics (H) Sem VIII (2025–26)")
st.write("by Pranjal")

# ---------------------------
# Semester Dates
# ---------------------------
default_start = datetime.date(2025, 12, 1)
default_end   = datetime.date(2026, 3, 21)

start_date = st.date_input("Semester Start Date", default_start)
end_date   = st.date_input("Semester End Date", default_end)

# ---------------------------
# Weekly Timetable Input
# ---------------------------
st.header("🗓 Weekly Timetable (write 2 entries for 2-hour classes)")

default_timetable = """Monday: Optical Fiber and Communication, Digital Electronics and Microprocessors, Advanced Materials Physics, Advanced Materials Physics
Tuesday: Digital Electronics and Microprocessors, Astronomical Techniques, Renewable Energy Economics, Astronomical Techniques, Astronomical Techniques
Wednesday: Space and Planetary Science, Digital Electronics and Microprocessors, Renewable Energy Economics, Optical Fiber and Communication
Thursday: Space and Planetary Science, Astronomical Techniques
Friday: Astronomical Techniques, Astronomical Techniques, Space and Planetary Science, Optical Fiber and Communication, Advanced Materials Physics, Advanced Materials Physics
"""

timetable_text = st.text_area("Enter weekly timetable:", default_timetable, height=220)

def parse_timetable(text):
    schedule={}
    for line in text.splitlines():
        if ":" in line:
            day,rest=line.split(":",1)
            subs=[s.strip() for s in rest.split(",") if s.strip()]
            schedule[day.strip()]=subs
    return schedule

schedule=parse_timetable(timetable_text)
subjects=set(s for subs in schedule.values() for s in subs)

# ---------------------------
# Holidays Text Input
# ---------------------------
st.header("🏖 Holidays (one date per line, YYYY-MM-DD)")

default_holidays = """2025-12-25
2025-12-26
2025-12-27
2025-12-28
2025-12-29
2025-12-30
2025-12-31
2026-01-01
2026-01-02
2026-01-03
2026-01-04
2026-01-05
"""

holiday_text = st.text_area("Enter all holidays:", default_holidays, height=180)

def parse_holidays(text):
    days=set()
    for line in text.splitlines():
        try:
            days.add(datetime.date.fromisoformat(line.strip()))
        except:
            pass
    return days

holidays_set=parse_holidays(holiday_text)

# ---------------------------
# Count Classes
# ---------------------------
counts={s:0 for s in subjects}
d=start_date
while d<=end_date:
    if d.weekday()<5 and d not in holidays_set:
        day=d.strftime("%A")
        for s in schedule.get(day,[]):
            counts[s]+=1
    d+=datetime.timedelta(days=1)

# ---------------------------
# Summary
# ---------------------------
st.header("📊 Total Classes")
st.table(pd.DataFrame([{"Subject":k,"Total Classes":v} for k,v in sorted(counts.items(),key=lambda x:-x[1])]))
