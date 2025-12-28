import streamlit as st
import datetime
import holidays
import pandas as pd
import pytesseract
import cv2
import numpy as np
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

st.set_page_config(page_title="Class Counter", layout="wide")
st.title("📚 Class Counter")
st.write("by Pranjal")

# ---------------------------
# IMAGE CLEANING
# ---------------------------
def preprocess_image(img):
    img = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2GRAY)
    img = cv2.threshold(img, 160, 255, cv2.THRESH_BINARY)[1]
    img = cv2.medianBlur(img, 3)
    return img

def extract_schedule_from_image(image):
    img = preprocess_image(Image.open(image))
    text = pytesseract.image_to_string(img, config="--psm 6")

    days = ["Monday","Tuesday","Wednesday","Thursday","Friday"]
    schedule = {d: [] for d in days}
    current_day = None

    for line in text.split("\n"):
        line = line.strip()

        for d in days:
            if d.lower() in line.lower():
                current_day = d

        if current_day and len(line) > 3:
            tokens = [w for w in line.split() if len(w) > 3]

            # Remove day names
            tokens = [t for t in tokens if t.lower() not in [d.lower() for d in days]]

            # Join tokens into subject names
            subject = " ".join(tokens)
            if subject and subject not in schedule[current_day]:
                schedule[current_day].append(subject)

    return schedule
# ---------------------------
# DATE INPUT
# ---------------------------
today = datetime.date.today()
start_date = st.date_input("Start Date", today)
end_date = st.date_input("End Date", today + datetime.timedelta(weeks=15))

# ---------------------------
# HOLIDAYS INDIA
# ---------------------------
holiday_list = holidays.India(years=range(start_date.year, end_date.year + 1))
if "holidays" not in st.session_state:
    st.session_state.holidays = {d: name for d, name in holiday_list.items() if start_date <= d <= end_date}

st.header("🏖 Manage Holidays")
holiday_df = pd.DataFrame([{"Date": d, "Holiday": n} for d, n in sorted(st.session_state.holidays.items())])
st.table(holiday_df)

# ---------------------------
# TIMETABLE IMAGE
# ---------------------------
st.header("📸 Upload Timetable Image")
image_file = st.file_uploader("Upload timetable image", type=["png","jpg","jpeg"])

if image_file:
    with st.spinner("Reading timetable..."):
        schedule = extract_schedule_from_image(image_file)
    st.success("Timetable extracted successfully.")
else:
    schedule = {d: [] for d in ["Monday","Tuesday","Wednesday","Thursday","Friday"]}

# ---------------------------
# WEEKLY EDITOR
# ---------------------------
st.header("🗓 Weekly Schedule")
all_subjects = set()
final_schedule = {}

for d, subs in schedule.items():
    st.subheader(d)
    final_schedule[d] = []
    for i, s in enumerate(subs):
        val = st.text_input(f"{d} Subject {i+1}", s, key=f"{d}_{i}")
        if val.strip():
            final_schedule[d].append(val)
            all_subjects.add(val)

# ---------------------------
# COUNT CLASSES
# ---------------------------
future = {s: 0 for s in all_subjects}
current = start_date

while current <= end_date:
    if current not in st.session_state.holidays:
        day = current.strftime("%A")
        if day in final_schedule:
            for s in final_schedule[day]:
                future[s] += 1
    current += datetime.timedelta(days=1)

# ---------------------------
# SUMMARY
# ---------------------------
st.header("📊 Final Class Summary")
st.table(pd.DataFrame(future.items(), columns=["Subject", "Total Classes"]))
