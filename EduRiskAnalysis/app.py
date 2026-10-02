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
/* ---------- Buttons ---------- */
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
}
</style>
""", unsafe_allow_html=True)

# Set page configuration
st.set_page_config(
    page_title="EduRisk Analytics - Lab 02",
    page_icon="🎓",
    layout="centered"
)

student_df = pd.DataFrame({
    "Student Name": ["Dara", "Sophea", "Vuthy", "Malis", "Rithy" , "Sreyneang", "Chan", "Bopha"],
    "Course": ["Python", "Statistics", "Python", "Database", "Web App" , "Database" , "Python" , "Statistics"],
    "Score": [85, 68, 45, 92, 58, 91, 72, 62],
    "Attendance": [90, 75, 50, 95, 60, 94, 80, 88],
    "Study Hours": [12, 8, 3, 15, 5, 14, 9, 7]
}) 

# Add risk level function
def get_risk_level(score, attendance):
    if score < 60 or attendance < 60:
        return "High Risk"
    elif score < 75 or attendance < 75:
        return "Medium Risk"
    else:
        return "Low Risk"

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
    st.subheader("Interactive Student Risk Monitoring Dashboard")
    st.write("Welcome to Lab 02.")
    st.write("In this lab, you  will use Streamlit widgets to explore student performance data.")
    st.success("Lab 02 app is running successfully!")

# Create the Dashboard page
elif selected_page == "Dashboard":
    st.title("Interactive Dashboard")
    st.write("Use the fillters below to explore student performance.")
    
    # Add course filter
    selected_course = st.selectbox("Select Course", ["All"] + list(student_df["Course"].unique()))
    
    # Add risk level filter
    selected_risk = st.selectbox("Select Risk Level", ["All", "Low Risk", "Medium Risk", "High Risk"])
    
    # Add Minimum Attendance Slider
    min_attendance = st.slider("Minimum Attendance ", 0, 100, 0) 
    
    # Add Minimum Score Slider
    min_score = st.slider("Minimum Score", 0, 100, 0)
    
    # Add Filtering Logic
    filtered_df = student_df.copy()
    if selected_course != "All":
        filtered_df = filtered_df[filtered_df["Course"] == selected_course]
    
    if selected_risk != "All":
        filtered_df = filtered_df[filtered_df["Risk Level"] == selected_risk]
        
    filtered_df = filtered_df[(filtered_df["Attendance"] >= min_attendance)]
    filtered_df = filtered_df[(filtered_df["Score"] >= min_score)]
    
    # Add Dashboard Metrics
    total_students = len(filtered_df)
    
    if len(filtered_df) > 0:
        average_score = filtered_df["Score"].mean()
        average_attendance = filtered_df["Attendance"].mean()
    else:
        average_score = 0
        average_attendance = 0
    
    high_risk_students = filtered_df[filtered_df["Risk Level"] == "High Risk"].shape[0]
    st.subheader("Dashboard Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Students", total_students)
    with col2:
        st.metric("Average Score", round(average_score, 2))
    with col3:
        st.metric("High Risk Attendance", f"{round(average_attendance, 2)}%")
    with col4:
        st.metric("High Risk", high_risk_students)
        
    # Add show or hide dataset checkbox
    show_data = st.checkbox("Show Filtered Data", True)
    
    if show_data:
        st.subheader("Filtered Student Dataset")
        st.dataframe(filtered_df)

        # Add download buttons 
        csv = filtered_df.to_csv(index=False)
        pdf_bytes = create_pdf_report(filtered_df, "filtered_student_data.pdf")

        # CSV download button
        st.download_button(
            label="📥Download Filtered Data as CSV",
            data=csv,
            file_name='filtered_student_data.csv',
            mime='text/csv',
        )
        # PDF download button
        st.download_button(
            label="📄Download Filtered Data as PDF",
            data=pdf_bytes,
            file_name="filtered_student_data.pdf",
            mime="application/pdf",
        )
    else:
        st.info("Filtered dataset is hidden.")
    
    # Add Student Score Chart
    st.subheader("Charts")
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.write("Student Scores")
        if len(filtered_df) > 0:
            score_chart = (filtered_df.set_index("Student Name")["Score"])
            st.bar_chart(score_chart)
        else:
            st.warning("No data available for score chart.")
    
    # Add Risk Level count Chart
    with chart_col2:
        st.write("Risk Level Count")
        if len(filtered_df) > 0:
            risk_count = filtered_df["Risk Level"].value_counts()
            st.bar_chart(risk_count)
        else:
            st.warning("No data available for risk chart.")

# Update the Student Data page
elif selected_page == "Student Data":
    st.title("Student Data") 
    
    total_students = len(student_df)
    average_score = student_df["Score"].mean()
    average_attendance = student_df["Attendance"].mean()
    high_risk_students = student_df[student_df["Risk Level"] == "High Risk"].shape[0]
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Students", total_students)
    with col2:
        st.metric("Average Score", round(average_score, 2))
    with col3:
        st.metric("Average Attendance", f"{round(average_attendance, 2)}%")
    with col4:
        st.metric("High Risk Students", high_risk_students)
    
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
    st.title("Student Risk Checker")
    
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
    st.write("This app is part of Lab 02.")
    st.write("Course: Web App Development for Data Science")
    st.write("Project Theme: EduRisk Analytics")
    st.write("Topic: Streamlit Interactive Dashboard")
    st.info("Ethics Reminder: Risk prediction should support students, not punish them.")
