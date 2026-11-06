import streamlit as st  # Web app framework for building the UI
import pandas as pd     # Data manipulation and analysis (DataFrames)
from io import BytesIO  # In-memory binary buffer, e.g. for generating files without saving to disk
import base64           # Encode binary data (like PDFs/Excel) as text for download links
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle  # PDF building blocks: document, table, and table styling
from reportlab.lib import colors  # Color definitions for table styling (backgrounds, grid lines, text)
from reportlab.lib.pagesizes import A4, landscape  # Page size (A4) and landscape orientation helper
import os  # File and path operations, environment variables

# Set background image for the app
def set_background(image_path):
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    # Detect file type for the correct MIME type
    ext = image_path.split(".")[-1].lower()
    mime = "jpeg" if ext in ("jpg", "jpeg") else ext

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/{mime};base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}

        /* Transparent top header so the image shows through */
        [data-testid="stHeader"] {{
            background: rgba(0, 0, 0, 0);
        }}

        /* Semi-transparent panel so text stays readable */
        .block-container {{
            background-color: rgba(255, 255, 255, 0.85);
            padding: 2rem;
            border-radius: 12px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
set_background("views/download.png") 

# Customize the sidebar and main content text color
st.markdown("""
<style>
/* Sidebar background */
[data-testid="stSidebar"] {
    background-color: #F5F7FA;
}

/* All sidebar text black */
[data-testid="stSidebar"] * {
    color: #000000 !important;
}

/* Collapse arrow icon */
[data-testid="stSidebar"] svg {
    fill: #000000 !important;
}
</style>
""", unsafe_allow_html=True)
st.markdown("""
<style>
.block-container h1,
.block-container h2,
.block-container h3,
.block-container p {
    color: #000000 !important;
}
</style>
""", unsafe_allow_html=True)
st.markdown("""
<style>
/* Buttons */
.stButton > button,
.stDownloadButton > button,
[data-testid="stFormSubmitButton"] > button {
    background-color: #D3D3D3;
    color: #000000;
    border: 1px solid #A9A9A9;
    border-radius: 8px;
}
.stButton > button:hover,
.stDownloadButton > button:hover,
[data-testid="stFormSubmitButton"] > button:hover {
    background-color: #BEBEBE;
    color: #000000;
    border-color: #808080;
}

/* Course and risk-level dropdowns */
[data-testid="stSelectbox"] [data-baseweb="select"] > div {
    background-color: #D3D3D3;
    color: #000000;
}
[data-baseweb="popover"] [role="option"] {
    background-color: #D3D3D3;
    color: #000000;
}

/* Chart panels */
[data-testid="stVegaLiteChart"] {
    background-color: #D3D3D3;
    border-radius: 8px;
    padding: 8px;
}
[data-testid="stVegaLiteChart"] svg text {
    font-weight: 700 !important;
}
</style>
""", unsafe_allow_html=True)

# Set page configuration
st.set_page_config(
    page_title="EduRisk Analytics - Lab 02",
    page_icon="🎓",
    layout="centered"
)

# Upload file csv data 
def load_student_data():
    try:
        data = pd.read_csv("students.csv")
        return data
    except FileNotFoundError:
        st.error(
            "students.csv was not found. Please place it in the same folder as app.py."
        )
        st.stop()

# Load student data
student_df = load_student_data()
        
# Add risk level function
def get_risk_level(score, attendance):
    if score < 60 or attendance < 60:
        return "High Risk"
    elif score < 75 or attendance < 75:
        return "Medium Risk"
    else:
        return "Low Risk"
    
student_df["Risk Level"] = student_df.apply(
    lambda row: get_risk_level(
        row["Score"],
        row["Attendance"]
    ),
    axis=1
)

# Create PDF report function
def create_pdf_report(df, filename):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=20,
        rightMargin=20,
        topMargin=20,
        bottomMargin=20,
    )

    table_data = [list(df.columns)] + df.values.tolist()
    table = Table(table_data)
    table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2E6F9F")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("GRID", (0, 0), (-1, -1), 1, colors.grey),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
        ])
    )

    doc.build([table])
    buffer.seek(0)
    return buffer.getvalue()

def style_dataframe(df):
    return df.style.set_properties(
        **{"background-color": "#D3D3D3", "color": "#000000"}
    ).set_table_styles([
        {
            "selector": "th, th.col_heading, th.row_heading, th.blank",
            "props": [("background-color", "#D3D3D3"), ("color", "#000000")],
        },
        {
            "selector": "td",
            "props": [("background-color", "#D3D3D3"), ("color", "#000000")],
        },
    ])


# Add risk level column
student_df["Risk Level"] = student_df.apply(lambda row: get_risk_level(row["Score"], row["Attendance"]), axis=1)

total_students = len(student_df)
average_score = student_df["Score"].mean()
average_attendance = student_df["Attendance"].mean()
low_score_students = student_df[student_df["Score"] < 60].shape[0]

# Update Sidebar Navigation
with st.sidebar:
    st.title("EduRisk Menu")
    selected_page = st.radio(
        "Select Page",
        ["Home", "Dashboard" ,"Student Data", "Risk Checker" ,"About"]
    )

# Update the Home page
if selected_page == "Home":
    st.title("🎓 EduRisk Analytics")
    st.subheader("Frontend Prototype with CSV Data Loading")
    st.write("Welcome to Lab 03.")
    st.write(
        "In this lab, the app loads student data from students.csv "
        "using Pandas instead of storing data directly inside app.py."
    )
    st.success("Lab 03 app is running successfully!")

# Create the Dashboard page
elif selected_page == "Dashboard":
    st.title("Dashboard Prototype")

    st.write(
        "This dashboard gives a quick overview of student performance "
        "using data loaded from students.csv."
    )

    total_students = len(student_df)
    average_score = student_df["Score"].mean()
    average_attendance = student_df["Attendance"].mean()
    high_risk_students = student_df[
        student_df["Risk Level"] == "High Risk"
    ].shape[0]

    st.subheader("Dashboard Metrics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Students", total_students)

    with col2:
        st.metric("Average Score", round(average_score, 2))

    with col3:
        st.metric("Average Attendance", f"{round(average_attendance, 2)}%")

    with col4:
        st.metric("High Risk", high_risk_students)

    st.subheader("Student Records")
    st.write("This table shows student data loaded from students.csv.")
    st.dataframe(student_df)
    csv = student_df.to_csv(index=False)
    pdf_bytes = create_pdf_report(student_df, "student_data.pdf")
    st.download_button(
        label="📥Download Full Data as CSV",
        data=csv,
        file_name="full_student_data.csv",
        mime="text/csv"
    )
    # PDF download button
    st.download_button(
        label="📄Download Full Data as PDF",
        data=pdf_bytes,
        file_name="full_student_data.pdf",
        mime="application/pdf"
    )

    st.subheader("Charts")

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.write("Student Score Chart")
        score_chart = student_df.set_index("Student Name")["Score"]
        st.bar_chart(score_chart)

    with chart_col2:
        st.write("Course Count")
        course_count = student_df["Course"].value_counts()
        st.bar_chart(course_count)

    st.info(
        "Ethics Reminder: Academic monitoring should support students, "
        "not label or punish them."
    )

# Update the Student Data page
elif selected_page == "Student Data":
    st.title("Student Data")

    st.write(
        "This page displays and inspects the dataset loaded from students.csv."
    )

    st.subheader("Data Inspection")

    st.write("Rows and Columns:", student_df.shape)

    st.write("Column Names:")
    st.write(student_df.columns.tolist())

    st.write("First 5 Rows:")
    st.dataframe(student_df.head())

    st.subheader("Full Student Dataset")
    st.dataframe(student_df)
    
    # Add download buttons
    csv = student_df.to_csv(index=False)
    pdf_bytes = create_pdf_report(student_df, "student_data.pdf")
    
    # CSV download button
    st.download_button(
        label="📥Download Full Data as CSV",
        data=csv,
        file_name="full_student_data.csv",
        mime="text/csv"
    )
    # PDF download button
    st.download_button(
        label="📄Download Full Data as PDF",
        data=pdf_bytes,
        file_name="full_student_data.pdf",
        mime="application/pdf"
    )

# Create the Risk Checker page
elif selected_page == "Risk Checker":
    st.title("Single Student Risk Checker")

    st.write(
        "Use this page to check the risk level of one student based on "
        "score and attendance."
    )

    with st.form("risk_checker_form"):
        input_name = st.text_input("Student Name")
        input_score = st.number_input("Score", 0, 100, 50)
        input_attendance = st.number_input("Attendance", 0, 100, 50)
        submitted = st.form_submit_button("Check Risk")

    if submitted:
        risk_result = get_risk_level(input_score, input_attendance)

        st.write("Student Name:", input_name)
        st.write("Score:", input_score)
        st.write("Attendance:", input_attendance)

        if risk_result == "Low Risk":
            st.success("Risk Level: Low Risk")
        elif risk_result == "Medium Risk":
            st.warning("Risk Level: Medium Risk")
        else:
            st.error("Risk Level: High Risk")
else:
    st.title("About")

    st.write("This app is part of Lab 03.")
    st.write("Course: Web App Development for Data Science")
    st.write("Project Theme: EduRisk Analytics")
    st.write("Topic: Data Loading, Layout, and Frontend Prototype")

    st.info(
        "This frontend prototype loads real data from students.csv "
        "and displays it using Streamlit and Pandas."
    )

    st.warning(
        "Ethics Reminder: Student risk information should be used responsibly "
        "to support learning and student success."
    )
