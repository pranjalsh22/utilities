import streamlit as st
import datetime
import holidays

# ---------------------------
# Default dates
# ---------------------------
today = datetime.date.today()
start_date = st.date_input("📅 Start Date", today)
end_date = st.date_input("📅 End Date", today + datetime.timedelta(weeks=15))

# ---------------------------
# Get Indian holidays in range
# ---------------------------
holiday_list = holidays.India(years=range(start_date.year, end_date.year + 1))
holidays_in_range = {d: name for d, name in holiday_list.items() if start_date <= d <= end_date}

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
for day, subjects in default_schedule.items():
    st.subheader(day)
    num_subjects = st.number_input(f"Number of subjects on {day}", min_value=0, max_value=10, value=len(subjects), key=f"{day}_num")
    
    schedule[day] = []
    for i in range(num_subjects):
        subj = st.text_input(f"{day} - Subject {i+1}", value=subjects[i] if i < len(subjects) else "", key=f"{day}_{i}")
        if subj.strip():
            schedule[day].append(subj)

# ---------------------------
# Generate timetable excluding holidays
# ---------------------------
st.header("🗓️ Final Timetable (Excludes Holidays)")

current_date = start_date
while current_date <= end_date:
    weekday = current_date.strftime("%A")
    
    if current_date in holidays_in_range:
        st.write(f"**{current_date} ({weekday})** - Holiday: 🎉 {holidays_in_range[current_date]}")
    elif weekday in schedule and schedule[weekday]:
        st.write(f"**{current_date} ({weekday})** - {', '.join(schedule[weekday])}")
    else:
        st.write(f"**{current_date} ({weekday})** - No classes")
    
    current_date += datetime.timedelta(days=1)

# ---------------------------
# Show list of holidays separately
# ---------------------------
st.header("🎊 Holidays in Selected Range")
for d, name in holidays_in_range.items():
    st.write(f"{d} - {name}")
