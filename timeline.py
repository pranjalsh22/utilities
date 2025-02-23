import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

# Define the Scientist class
class Scientist:
    def __init__(self, name, start, end, description, fields):
        self.name = name
        self.start = pd.to_datetime(start)
        self.end = pd.to_datetime(end)
        self.description = description
        self.fields = fields

    def __repr__(self):
        return f"Scientist(name={self.name}, start={self.start}, end={self.end}, fields={self.fields})"

    # Method to convert the object back to a dict for saving in JSON
    def to_dict(self):
        return {
            "name": self.name,
            "start": self.start.strftime('%Y-%m-%d'),
            "end": self.end.strftime('%Y-%m-%d'),
            "description": self.description,
            "fields": self.fields
        }

# Path to the JSON file where data will be saved
DATA_FILE = "scientists_data.json"

# Authenticate with Google
def authenticate_google_drive():
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()  # Creates local webserver and auto handles authentication.
    drive = GoogleDrive(gauth)
    return drive

# Load data from Google Drive
def load_scientists_from_google_drive(drive):
    file_list = drive.ListFile({'q': "title='scientists_data.json'"}).GetList()
    if file_list:
        file = file_list[0]
        file.GetContentFile('scientists_data.json')
        with open('scientists_data.json', 'r') as file:
            data = json.load(file)
        return [Scientist(s["name"], s["start"], s["end"], s["description"], s["fields"]) for s in data]
    return []

# Save data to Google Drive
def save_scientists_to_google_drive(scientists_list, drive):
    data = [s.to_dict() for s in scientists_list]
    file = drive.CreateFile({'title': 'scientists_data.json'})
    file.Upload()  # Upload the file to Google Drive

# Load existing scientists data
drive = authenticate_google_drive()
scientists = load_scientists_from_google_drive(drive)

# Sidebar: Add new scientist
st.sidebar.subheader("Add New Scientist")
name = st.sidebar.text_input("Name")
start_date = st.sidebar.date_input("Start Date")
end_date = st.sidebar.date_input("End Date")
description = st.sidebar.text_area("Description")
fields = st.sidebar.multiselect("Fields of Study", ["Physics", "Mathematics", "Astrophysics", "Chemistry", "Biology", "Engineering", "Computer Science"])

# Add the new scientist when the "Add Scientist" button is clicked
if st.sidebar.button("Add Scientist"):
    if name and start_date and end_date and description and fields:
        new_scientist = Scientist(name, start_date, end_date, description, fields)
        scientists.append(new_scientist)
        save_scientists_to_google_drive(scientists, drive)  # Save updated data to Google Drive
        st.sidebar.success(f"Scientist {name} added successfully!")
    else:
        st.sidebar.warning("Please fill in all fields.")

# Sidebar: Edit or remove scientist
st.sidebar.subheader("Edit or Remove Scientist")
edit_name = st.sidebar.selectbox("Select Scientist to Edit", [s.name for s in scientists])

if edit_name:
    scientist_to_edit = next(s for s in scientists if s.name == edit_name)
    
    # Display current values
    new_name = st.sidebar.text_input("Edit Name", value=scientist_to_edit.name)
    new_start_date = st.sidebar.date_input("Edit Start Date", value=scientist_to_edit.start.date())
    new_end_date = st.sidebar.date_input("Edit End Date", value=scientist_to_edit.end.date())
    new_description = st.sidebar.text_area("Edit Description", value=scientist_to_edit.description)
    new_fields = st.sidebar.multiselect("Edit Fields of Study", ["Physics", "Mathematics", "Astrophysics", "Chemistry", "Biology", "Engineering", "Computer Science"], default=scientist_to_edit.fields)
    
    if st.sidebar.button("Update Scientist"):
        scientist_to_edit.name = new_name
        scientist_to_edit.start = pd.to_datetime(new_start_date)
        scientist_to_edit.end = pd.to_datetime(new_end_date)
        scientist_to_edit.description = new_description
        scientist_to_edit.fields = new_fields
        save_scientists_to_google_drive(scientists, drive)  # Save updated data to Google Drive
        st.sidebar.success(f"Scientist {new_name} updated successfully!")

# Remove scientist
if st.sidebar.button("Remove Scientist"):
    if edit_name:
        scientists = [s for s in scientists if s.name != edit_name]
        save_scientists_to_google_drive(scientists, drive)  # Save updated data to Google Drive
        st.sidebar.success(f"Scientist {edit_name} removed successfully!")
    else:
        st.sidebar.warning("No scientist selected to remove.")

# Sidebar: Select fields to display
fields_available = list(set([field for sublist in [s.fields for s in scientists] for field in sublist]))
selected_fields = st.sidebar.multiselect("Select fields", fields_available, default=fields_available)

# Convert scientists list to DataFrame
df = pd.DataFrame([{
    "name": s.name,
    "start": s.start,
    "end": s.end,
    "description": s.description,
    "fields": s.fields
} for s in scientists])

# Filter the scientists based on selected fields
filtered_df = df[df['fields'].apply(lambda x: any(field in selected_fields for field in x))]

# Sort by start date
filtered_df = filtered_df.sort_values(by='start')

# Create a timeline plot
timeline_fig = px.timeline(filtered_df, 
                           x_start="start", 
                           x_end="end", 
                           y="name", 
                           color="fields", 
                           title="Scientist Timeline",
                           labels={"name": "Scientist", "fields": "Fields of Study"})

timeline_fig.update_yaxes(categoryorder="total ascending")  # To sort the scientists in order
timeline_fig.update_layout(showlegend=True)

# Display the timeline
st.plotly_chart(timeline_fig)

# Show detailed information on each scientist
for _, row in filtered_df.iterrows():
    st.subheader(row['name'])
    st.write(f"**Lifespan**: {row['start'].strftime('%B %d, %Y')} - {row['end'].strftime('%B %d, %Y')}")
    st.write(f"**Fields**: {', '.join(row['fields'])}")
    st.write(f"**Description**: {row['description']}")
