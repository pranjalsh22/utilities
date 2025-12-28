import streamlit as st
import datetime
import holidays
import pandas as pd
import base64
from openai import OpenAI

# ---------------------------
# PAGE CONFIG
# ---------------------------
st.set_page_config(page_title="Class Counter", layout="wide")
st.title("📚 Class Counter")
st.write("by Pranjal")

# ---------------------------
# OPENAI CLIENT
# ---------------------------
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def extract_schedule_from_image(image_file):
    try:
        image_bytes = image_file.read()
        encoded = base64.b64encode(image_bytes).decode()

        prompt = """
        Extract weekly timetable from this image.
        Return ONLY valid JSON in this format:
        {
          "Monday": [],
          "Tuesday": [],
          "Wednesday": [],
          "Thursday": [],
          "Friday": []
        }
        """

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": encoded
                        }
                    }
                ]
            }]
        )

        return eval(response.output_text.strip())

    except Exception as e:
        st.error("❌ Failed to analyze image. Please check your API key and retry.")
        st.stop()

# ---------------------------
# DATE INPUTS
# ---------------------------
today = datetime.date.today()
start_date = st.date_input("Start Date", today)
end_date = st.date_input("End Date", today + datetime.timedelta(weeks=15))

# ---------------------------
# HOLIDAYS INDIA
# ---------------------------
holiday_list = holidays.India(years=range(start_date.year, end_date.year + 1))
auto_holidays = {d: name for d, name in holiday_list.items() if start_date <= d <= end_date}

if "holidays" not in st.session_state:
    st.session_state.holidays = dict(auto_holidays)

st.header("🏖 Manage Holidays")

if st.session_state.holidays:
    holiday_df = pd.DataFrame(
        [{"Date": d, "Holiday": name} for d, name in sorted(st.session_state.holidays.items())]
    )
    st.table(holiday_df)

col1, col2 = st.columns(2)
with col1:
    new_holiday_date = st.date_input("➕ Add custom holiday", today, key="new_holiday")
    new_holiday_name = st.text_input("Holiday name", value="Custom Holiday")
    if st.button("Add Holiday"):
        st.session_state.holidays[new_holiday_date] = new_holiday_name

with col2:
    if st.session_state.holidays:
        remove_date = st.selectbox("Remove holiday", list(st.session_state.holidays.keys()))
        if st.button("Remove Selected Holiday"):
            st.session_state.holidays.pop(remove_date, None)

# ---------------------------
# TIMETABLE IMAGE
# ---------------------------
st.header("📸 Upload Timetable Image")
image_file = st.file_uploader("Upload timetable image", type=["png","jpg","jpeg"])

if image_file:
    with st.spinner("Analyzing timetable..."):
        default_schedule = extract_schedule_from_image(image_file)
    st.success("Timetable extracted successfully.")
else:
    default_schedule = {d: [] for d in ["Monday","Tuesday","Wednesday","Thursday","Friday"]}

# ---------------------------
# WEEKLY SCHEDULE EDITOR
# ---------------------------
st.header("🗓 Weekly Schedule")
schedule = {}
all_subjects = set()

for day, subjects in default_schedule.items():
    st.subheader(day)
    num = st.number_input(f"Number of subjects on {day}", 0, 10, len(subjects), key=f"{day}_num")
    schedule[day] = []
    for i in range(num):
        subj = st.text_input(f"{day} Subject {i+1}", subjects[i] if i < len(subjects) else "", key=f"{day}_{i}")
        if subj.strip():
            schedule[day].append(subj)
            all_subjects.add(subj)

# ---------------------------
# COMPLETED CLASSES
# ---------------------------
st.header("✔ Already Completed Classes")
completed = {}
for s in sorted(all_subjects):
    completed[s] = st.number_input(s, min_value=0, value=0)

# ---------------------------
# COUNT FUTURE CLASSES
# ---------------------------
future = {s:0 for s in all_subjects}
current = start_date

while current <= end_date:
    if current not in st.session_state.holidays:
        day = current.strftime("%A")
        if day in schedule:
            for s in schedule[day]:
                future[s] += 1
    current += datetime.timedelta(days=1)

# ---------------------------
# FINAL SUMMARY
# ---------------------------
st.header("📊 Final Class Summary")

rows=[]
for s in sorted(all_subjects):
    rows.append({
        "Subject": s,
        "Completed": completed[s],
        "Upcoming": future[s],
        "Total": completed[s]+future[s]
    })

st.table(pd.DataFrame(rows))
