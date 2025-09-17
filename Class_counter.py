import streamlit as st
import pandas as pd
from datetime import date, timedelta
from openai import OpenAI

st.set_page_config(page_title="Class Counter", layout="centered")

st.title(" Class Counter by Pranjal")

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["openai"]["api_key"])

# Step 1: Subject setup
st.header("Step 1: Define Subjects and Weekly Schedule")

num_subjects = st.number_input("How many subjects?", min_value=1, max_value=10, value=3, step=1)
subjects = {}

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

for i in range(num_subjects):
    st.subheader(f"Subject {i+1}")
    subject_name = st.text_input(f"Enter subject name {i+1}", key=f"name_{i}")
    weekly_schedule = {}
    cols = st.columns(5)
    for j, day in enumerate(days):
        unique_key = f"subject_{i}_day_{day}"
        weekly_schedule[day] = cols[j].number_input(
            f"{day}", min_value=0, max_value=10, value=0, key=unique_key
        )
    completed = st.number_input(
        f"Number of classes already completed in {subject_name or f'Subject {i+1}'}",
        min_value=0, value=0, key=f"done_{i}"
    )
    subjects[f"Subject_{i}_{subject_name}"] = {
        "name": subject_name or f"Subject {i+1}",
        "weekly_schedule": weekly_schedule,
        "completed": completed
    }

# Step 2: Date inputs
st.header("Step 2: Set Date Range")

start_date = st.date_input("Start date", value=date.today())
end_date = st.date_input("End date", value=date.today() + timedelta(weeks=15))

# Step 3: Days off (calendar-based)
st.header("Step 3: Add Days Off (Holidays, Breaks)")

if "off_days" not in st.session_state:
    st.session_state.off_days = set()

# --- Manual add ---
new_off_day = st.date_input("📅 Pick a day off", value=date.today())

col1, col2 = st.columns(2)
if col1.button("➕ Add this day off"):
    st.session_state.off_days.add(new_off_day)
if col2.button("🗑️ Clear all days off"):
    st.session_state.off_days.clear()

# --- GPT Suggestion ---
st.markdown("#### ✨ Auto-suggest holidays with AI")
if st.button("Suggest Holidays with ChatGPT"):
    prompt = f"""
    List all major public holidays in India (national + widely observed festivals)
    between {start_date} and {end_date}. 
    Return them in JSON format as a list of dates (YYYY-MM-DD) with holiday names.
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    suggestion = response.choices[0].message.content

    st.subheader("Suggested Holidays")
    st.code(suggestion, language="json")

    # If you want, you can parse the JSON into actual dates
    import json
    try:
        holidays = json.loads(suggestion)
        for h in holidays:
            holiday_date = date.fromisoformat(h["date"])
            st.session_state.off_days.add(holiday_date)
        st.success("✅ Added suggested holidays to off days!")
    except Exception:
        st.error("Could not parse GPT response. Please check formatting.")

# Display selected off days
if st.session_state.off_days:
    sorted_days = sorted(st.session_state.off_days)
    st.markdown("### 📌 Selected Days Off:")
    st.write(sorted_days)
else:
    st.info("No off days selected yet.")

# Step 4: Results
st.header(" Result: Projected Class Counts by End Date")

if st.button("Calculate"):
    total_future_classes = {key: 0 for key in subjects}

    current_date = start_date
    while current_date <= end_date:
        if current_date in st.session_state.off_days:
            current_date += timedelta(days=1)
            continue
        weekday = current_date.strftime("%A")
        for key, info in subjects.items():
            total_future_classes[key] += info["weekly_schedule"].get(weekday, 0)
        current_date += timedelta(days=1)

    # Display results
    results = []
    for key, info in subjects.items():
        completed = info["completed"]
        expected = total_future_classes[key]
        total_by_end = completed + expected
        results.append({
            "Subject": info["name"],
            "Classes Already Completed": completed,
            "Classes Expected (From Today)": expected,
            "Total Classes by End Date": total_by_end
        })

    df = pd.DataFrame(results)
    st.dataframe(df, use_container_width=True)
