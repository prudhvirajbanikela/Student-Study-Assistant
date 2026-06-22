import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
page_title="Student Performance Dashboard",
layout="wide"
)

st.title("📊 Student Performance Analytics Dashboard")

# Load Dataset

df = pd.read_csv("data/Indian_Student_Performance_1000.csv")

# =====================

# DATA PREVIEW

# =====================

st.subheader("📌 Dataset Preview")
st.dataframe(df.head())

# =====================

# KPI CARDS

# =====================

col1, col2, col3, col4 = st.columns(4)

col1.metric(
"Total Students",
len(df)
)

col2.metric(
"Avg Exam Score",
round(df["Exam_Score"].mean(), 2)
)

col3.metric(
"Avg Attendance",
round(df["Attendance_Percent"].mean(), 2)
)

pass_rate = (
(df["Pass_Fail"] == "Pass").mean() * 100
)

col4.metric(
"Pass Rate",
f"{pass_rate:.2f}%"
)

# =====================

# GENDER DISTRIBUTION

# =====================

st.subheader("👨‍🎓 Gender Distribution")

fig1 = px.pie(
df,
names="Gender",
title="Gender Distribution"
)

st.plotly_chart(fig1, use_container_width=True)

# =====================

# CITY DISTRIBUTION

# =====================

st.subheader("🏙 Students by City")

city_count = (
df["City"]
.value_counts()
.reset_index()
)

city_count.columns = ["City", "Count"]

fig2 = px.bar(
city_count,
x="City",
y="Count",
title="Students by City"
)

st.plotly_chart(fig2, use_container_width=True)

# =====================

# STUDY HOURS VS EXAM

# =====================

st.subheader("📈 Study Hours vs Exam Score")

fig3 = px.scatter(
df,
x="Study_Hours",
y="Exam_Score",
color="Gender",
hover_name="Student_Name"
)

st.plotly_chart(fig3, use_container_width=True)

# =====================

# ATTENDANCE VS EXAM

# =====================

st.subheader("📊 Attendance vs Exam Score")

fig4 = px.scatter(
df,
x="Attendance_Percent",
y="Exam_Score",
color="Pass_Fail"
)

st.plotly_chart(fig4, use_container_width=True)

# =====================

# EXAM SCORE DISTRIBUTION

# =====================

st.subheader("📚 Exam Score Distribution")

fig5 = px.histogram(
df,
x="Exam_Score",
nbins=20
)

st.plotly_chart(fig5, use_container_width=True)

# =====================

# TOP 10 STUDENTS

# =====================

st.subheader("🏆 Top 10 Students")

top_students = (
df.sort_values(
by="Exam_Score",
ascending=False
)
.head(10)
)

st.dataframe(
top_students[
[
"Student_Name",
"City",
"Exam_Score",
"Attendance_Percent"
]
]
)
