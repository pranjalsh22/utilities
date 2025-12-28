import streamlit as st
import pandas as pd
from PIL import Image
from datetime import datetime
import os
import pytesseract

pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"
# ------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------
st.set_page_config(page_title="Timetable Class Counter", layout="wide")
st.title("📅 Semester Timetable Class Counter")

# ------------------------------------------------------
# OCR FUNCTION
# ------------------------------------------------------
def extract_text(image):
    img = Image.open(image)
    return pytesseract.image_to_string(img)

# ------------------------------------------------------
# PARSE WEEKLY SCHEDULE
# ------------------------------------------------------
def parse_schedule(text):
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    schedule = {d: [] for d in days}
    current_day = None

    for line in text.split("\n"):
        for d in days:
            if d.lower() in line.lower():
                current_day = d

        if current_day:
            words = [w.strip() for w in line.split() if len(w.strip()) > 4]
            for w in words:
                if w.isalpha():
                    schedule[current_day].append(w)

    return schedule

# ------------------------------------------------------
# GENERATE WORKING DAYS
# ------------------------------------------------------
def generate_working_days(start, end):
    all_days = pd.date_range(start, end)
    return [d for d in all_days if d.weekday() < 5]

# ------------------------------------------------------
# EXPAND HOLIDAY RANGES
# ------------------------------------------------------
def expand_holidays(ranges):
    holidays = set()
    for s, e in ranges:
        for d in pd.date_range(s, e):
            holidays.add(d)
    return holidays

# ------------------------------------------------------
# COUNT CLASSES
# ------------------------------------------------------
def count_classes(days, schedule):
    counts = {}
    for d in days:
        weekday = d.strftime("%A")
        if weekday in schedule:
            for subject in schedule[weekday]:
                counts[subject] = counts.get(subject, 0) + 1
    return counts

# ------------------------------------------------------
# UI INPUTS
# ------------------------------------------------------
col1, col2 = st.columns(2)
with col1:
    image_file = st.file_uploader("Upload Timetable Image", type=["png","jpg","jpeg"])
with col2:
    start_date = st.date_input("Semester Start Date")
    end_date   = st.date_input("Semester End Date")

st.subheader("🏖 Add Holidays")
holiday_text = st.text_area(
    "Format: YYYY-MM-DD to YYYY-MM-DD (one per line)",
    "2025-12-25 to 2026-01-02"
)

# ------------------------------------------------------
# PROCESS BUTTON
# ------------------------------------------------------
if st.button("📊 Calculate Total Classes") and image_file:

    text = extract_text(image_file)
    schedule = parse_schedule(text)

    working_days = generate_working_days(start_date, end_date)

    ranges = []
    for line in holiday_text.splitlines():
        if "to" in line:
            s,e = line.split("to")
            ranges.append((pd.to_datetime(s.strip()), pd.to_datetime(e.strip())))

    holidays = expand_holidays(ranges)
    final_days = [d for d in working_days if d not in holidays]

    counts = count_classes(final_days, schedule)

    # ------------------------------------------------------
    # OUTPUTS
    # ------------------------------------------------------
    st.subheader("📌 Weekly Schedule Detected")
    st.write(schedule)

    st.subheader("🗓 Total Working Days")
    st.success(len(final_days))

    st.subheader("📚 Total Classes Per Subject")
    df = pd.DataFrame(counts.items(), columns=["Subject", "Total Classes"])
    st.dataframe(df, use_container_width=True)

    st.subheader("🚫 Excluded Holiday Dates")
    st.write(sorted(list(holidays)))
