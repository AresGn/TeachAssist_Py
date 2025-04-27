# TeachAssist - Student Submission Portal

A Streamlit web application for students to submit Java assignments in ZIP format with deadlines.

## Features

- **Student Portal**
  - Submit Java assignments as ZIP files
  - View assignment details and deadlines
  - Automatic validation of ZIP files for Java content

- **Teacher Dashboard**
  - Create and manage assignments
  - Set deadlines for submissions
  - View and download student submissions
  - Simple password protection

## Setup and Installation

1. Make sure Python is installed on your system
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
3. Run the application:
   ```
   streamlit run app.py
   ```

## Usage

### For Students
1. Navigate to the "Student Submission" page
2. Enter your Student ID and Full Name
3. Select an assignment from the dropdown
4. Upload your Java project as a ZIP file
5. Submit before the deadline

### For Teachers
1. Navigate to the "Teacher Dashboard" page
2. Enter the teacher password (default: "teachassist")
3. Create new assignments with descriptions and deadlines
4. View all student submissions organized by assignment

## Directory Structure

```
submission_portal/
├── app.py                   # Main Streamlit application
├── uploads/                 # Directory to store student submissions
├── data/                    # Directory for application data
│   ├── assignments.csv      # Stores assignment information
│   └── submissions.csv      # Stores submission information
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

## Notes
- Teacher password is set to "teachassist" for demonstration purposes
- In a production environment, proper authentication should be implemented 