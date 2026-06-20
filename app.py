import streamlit as st
import joblib
import pandas as pd
import matplotlib.pyplot as plt

# Page config
st.set_page_config(
    page_title="AI Student Assistant",
    page_icon="🎓",
    layout="centered"
)

# Load model
model = joblib.load("student_model.pkl")

# Custom styling
st.markdown(
    """
    <style>
    .main {
        background-color: #0f172a;
        color: white;
    }

    h1 {
        text-align: center;
        color: #38bdf8;
    }

    .stButton>button {
        background-color: #38bdf8;
        color: white;
        border-radius: 10px;
        height: 3em;
        width: 100%;
        font-size: 18px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Title
st.title("🎓 AI-Powered Student Study Assistant")

st.write("Predict your academic performance using Machine Learning")

# Sidebar
st.sidebar.header("Student Inputs")

hours = st.sidebar.slider("Study Hours", 1, 12, 5)
attendance = st.sidebar.slider("Attendance %", 40, 100, 75)
difficulty = st.sidebar.slider("Subject Difficulty", 1, 10, 5)

# Prediction
if st.button("Predict Score"):

    input_data = pd.DataFrame(
        [[hours, attendance, difficulty]],
        columns=["Hours", "Attendance", "Difficulty"]
    )

    prediction = model.predict(input_data)
    score = prediction[0]

    st.success(f"📊 Predicted Score: {score:.2f}")

    # Suggestions
    if score >= 85:
        st.info("🔥 Excellent preparation! Keep going.")
    elif score >= 60:
        st.warning("⚡ Good performance, but improve consistency.")
    else:
        st.error("📚 Need more focus and study time.")

    # Chart
    st.subheader("Performance Analysis")

    categories = ["Study Hours", "Attendance", "Difficulty", "Predicted Score"]
    values = [hours, attendance, difficulty, score]

    fig, ax = plt.subplots()
    ax.bar(categories, values)

    st.pyplot(fig)

# Footer
st.markdown("---")
st.caption("Built with Python, Streamlit & Machine Learning")