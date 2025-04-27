import streamlit as st
import os
import zipfile
import datetime
import pandas as pd
from pathlib import Path

# Set page config
st.set_page_config(
    page_title="TeachAssist - Student Submission Portal",
    page_icon="📚",
    layout="wide"
)

# Create directories for storing submissions
UPLOAD_DIR = Path("submission_portal/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Load or create assignments data
ASSIGNMENTS_FILE = Path("submission_portal/data/assignments.csv")
ASSIGNMENTS_FILE.parent.mkdir(parents=True, exist_ok=True)

if ASSIGNMENTS_FILE.exists():
    assignments_df = pd.read_csv(ASSIGNMENTS_FILE)
else:
    assignments_df = pd.DataFrame({
        "id": [],
        "title": [],
        "description": [],
        "deadline": [],
        "created_at": []
    })
    assignments_df.to_csv(ASSIGNMENTS_FILE, index=False)

# Load or create submissions data
SUBMISSIONS_FILE = Path("submission_portal/data/submissions.csv")
if SUBMISSIONS_FILE.exists():
    submissions_df = pd.read_csv(SUBMISSIONS_FILE)
else:
    submissions_df = pd.DataFrame({
        "student_id": [],
        "student_name": [],
        "assignment_id": [],
        "filename": [],
        "submitted_at": [],
        "file_path": []
    })
    submissions_df.to_csv(SUBMISSIONS_FILE, index=False)

# App title and description
st.title("TeachAssist - Student Submission Portal")
st.markdown("### Upload your Java assignments in ZIP format")

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Student Submission", "Teacher Dashboard"])

if page == "Student Submission":
    st.header("Submit Assignment")
    
    # Form for student submission
    with st.form("submission_form"):
        student_id = st.text_input("Student ID", help="Enter your university ID")
        student_name = st.text_input("Full Name", help="Enter your full name")
        
        # Initialize variables
        assignment_option = None
        deadline_passed = True
        uploaded_file = None
        
        # Show available assignments with deadlines
        if len(assignments_df) > 0:
            assignment_options = assignments_df["title"].tolist()
            assignment_option = st.selectbox("Select Assignment", options=assignment_options)
            selected_assignment = assignments_df[assignments_df["title"] == assignment_option].iloc[0]
            
            # Show assignment details
            st.markdown(f"**Description:** {selected_assignment['description']}")
            deadline = datetime.datetime.strptime(selected_assignment['deadline'], "%Y-%m-%d %H:%M:%S")
            st.markdown(f"**Deadline:** {deadline.strftime('%d %B %Y, %H:%M')}")
            
            # Calculate time remaining
            now = datetime.datetime.now()
            time_left = deadline - now
            
            if time_left.total_seconds() > 0:
                days_left = time_left.days
                hours_left = time_left.seconds // 3600
                minutes_left = (time_left.seconds % 3600) // 60
                st.info(f"Time remaining: {days_left} days, {hours_left} hours, {minutes_left} minutes")
                deadline_passed = False
                
                # File uploader
                uploaded_file = st.file_uploader("Upload Java Project (ZIP file only)", type="zip")
            else:
                st.error("The deadline for this assignment has passed!")
        else:
            st.info("No assignments available for submission at this time.")
        
        # Submit button (always shown)
        submit_button = st.form_submit_button("Submit Assignment")
        
        # Process the form submission
        if submit_button:
            if len(assignments_df) == 0:
                st.error("No assignments available for submission")
            elif deadline_passed:
                st.error("Cannot submit after the deadline has passed")
            elif uploaded_file is None:
                st.error("Please upload a ZIP file")
            elif not student_id or not student_name:
                st.error("Please enter your Student ID and Full Name")
            else:
                # Create directory for this student if it doesn't exist
                student_dir = UPLOAD_DIR / student_id
                student_dir.mkdir(exist_ok=True)
                
                # Save file
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                file_path = student_dir / f"{timestamp}_{uploaded_file.name}"
                
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Validate zip file contains Java files
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    file_list = zip_ref.namelist()
                    has_java = any(file.endswith('.java') for file in file_list)
                
                if has_java:
                    # Add submission to dataframe
                    new_submission = pd.DataFrame({
                        "student_id": [student_id],
                        "student_name": [student_name],
                        "assignment_id": [selected_assignment['id']],
                        "filename": [uploaded_file.name],
                        "submitted_at": [datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                        "file_path": [str(file_path)]
                    })
                    
                    submissions_df = pd.concat([submissions_df, new_submission], ignore_index=True)
                    submissions_df.to_csv(SUBMISSIONS_FILE, index=False)
                    
                    st.success("Assignment submitted successfully!")
                else:
                    st.error("The ZIP file does not contain any Java files. Please upload a valid Java project.")
                    # Remove the invalid file
                    os.remove(file_path)

elif page == "Teacher Dashboard":
    st.header("Teacher Dashboard")
    
    # Teacher authentication (simple for demonstration)
    teacher_password = st.sidebar.text_input("Teacher Password", type="password")
    if teacher_password == "teachassist":  # Simple password for demo
        tab1, tab2 = st.tabs(["Manage Assignments", "View Submissions"])
        
        with tab1:
            st.subheader("Create New Assignment")
            with st.form("assignment_form"):
                assignment_title = st.text_input("Assignment Title")
                assignment_desc = st.text_area("Assignment Description")
                deadline_date = st.date_input("Deadline Date")
                deadline_time = st.time_input("Deadline Time")
                
                submit_button = st.form_submit_button("Create Assignment")
                
                if submit_button:
                    if assignment_title and assignment_desc:
                        # Create deadline datetime
                        deadline_datetime = datetime.datetime.combine(deadline_date, deadline_time)
                        
                        # Generate assignment ID
                        assignment_id = len(assignments_df) + 1
                        
                        # Add assignment to dataframe
                        new_assignment = pd.DataFrame({
                            "id": [assignment_id],
                            "title": [assignment_title],
                            "description": [assignment_desc],
                            "deadline": [deadline_datetime.strftime("%Y-%m-%d %H:%M:%S")],
                            "created_at": [datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
                        })
                        
                        assignments_df = pd.concat([assignments_df, new_assignment], ignore_index=True)
                        assignments_df.to_csv(ASSIGNMENTS_FILE, index=False)
                        
                        st.success(f"Assignment '{assignment_title}' created successfully!")
                    else:
                        st.error("Please fill in all fields")
            
            st.subheader("Existing Assignments")
            if len(assignments_df) > 0:
                for _, row in assignments_df.iterrows():
                    with st.expander(f"{row['title']} (Due: {row['deadline']})"):
                        st.write(f"**Description:** {row['description']}")
                        st.write(f"**Created:** {row['created_at']}")
                        if st.button(f"Delete Assignment {row['id']}", key=f"del_{row['id']}"):
                            assignments_df = assignments_df[assignments_df['id'] != row['id']]
                            assignments_df.to_csv(ASSIGNMENTS_FILE, index=False)
                            st.experimental_rerun()
            else:
                st.info("No assignments created yet.")
        
        with tab2:
            st.subheader("Student Submissions")
            if len(submissions_df) > 0:
                # Group by assignment
                grouped = submissions_df.groupby("assignment_id")
                
                for assignment_id, group in grouped:
                    try:
                        assignment_title = assignments_df[assignments_df["id"] == assignment_id]["title"].iloc[0]
                        with st.expander(f"Assignment: {assignment_title} ({len(group)} submissions)"):
                            st.dataframe(
                                group[["student_id", "student_name", "filename", "submitted_at"]],
                                use_container_width=True
                            )
                            
                            # Download button for all submissions
                            if st.button(f"Download All Submissions for {assignment_title}", key=f"dl_{assignment_id}"):
                                st.info("Feature not implemented in this demo. In a real application, this would create a ZIP file with all submissions.")
                    except:
                        st.error(f"Could not find assignment with ID {assignment_id}")
            else:
                st.info("No submissions yet.")
    else:
        st.warning("Please enter the teacher password to access the dashboard")

st.sidebar.markdown("---")
st.sidebar.info("TeachAssist © 2023") 