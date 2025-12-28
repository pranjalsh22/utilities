import streamlit as st
import datetime
import holidays
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
# Timetable Input
# ---------------------------
st.header("🗓 Weekly Timetable (write 2 entries for 2-hour classes)")

default_text = """Monday: Optical Fiber and Communication, Digital Electronics and Microprocessors, Advanced Materials Physics, Advanced Materials Physics
Tuesday: Digital Electronics and Microprocessors, Astronomical Techniques, Renewable Energy Economics, Astronomical Techniques, Astronomical Techniques
Wednesday: Space and Planetary Science, Digital Electronics and Microprocessors, Renewable Energy Economics, Optical Fiber and Communication
Thursday: Space and Planetary Science, Astronomical Techniques
Friday: Astronomical Techniques, Astronomical Techniques, Space and Planetary Science, Optical Fiber and Communication, Advanced Materials Physics, Advanced Materials Physics
"""

timetable_text = st.text_area("Enter weekly timetable:", default_text, height=220)

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
# Holidays
# ---------------------------
holiday_list = holidays.India(years=range(start_date.year, end_date.year+1))
auto_holidays={d:n for d,n in holiday_list.items() if start_date<=d<=end_date}

winter_start=datetime.date(2025,12,25)
winter_end=datetime.date(2026,1,5)

d=winter_start
while d<=winter_end:
    auto_holidays[d]="Winter Break"
    d+=datetime.timedelta(days=1)

if "holidays" not in st.session_state:
    st.session_state.holidays=dict(auto_holidays)

st.header("🏖 Manage Holidays")
st.table(pd.DataFrame([{"Date":d,"Holiday":n} for d,n in st.session_state.holidays.items()]))

# ---------------------------
# Count Classes
# ---------------------------
counts={s:0 for s in subjects}
d=start_date
while d<=end_date:
    if d.weekday()<5 and d not in st.session_state.holidays:
        day=d.strftime("%A")
        for s in schedule.get(day,[]):
            counts[s]+=1
    d+=datetime.timedelta(days=1)

# ---------------------------
# Summary
# ---------------------------
st.header("📊 Total Classes")
st.table(pd.DataFrame([{"Subject":k,"Total Classes":v} for k,v in sorted(counts.items(),key=lambda x:-x[1])]))
