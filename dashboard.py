import streamlit as st
import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# ---------------- FILE PATHS ----------------
USER_FILE = "users.csv"
HISTORY_FILE = "history.csv"

# ---------------- SAFE LOAD FUNCTIONS ----------------
def load_users():
    try:
        df = pd.read_csv(USER_FILE)
        if df.empty or "username" not in df.columns:
            raise ValueError
        return df
    except:
        df = pd.DataFrame(columns=["username", "password"])
        df.to_csv(USER_FILE, index=False)
        return df

def load_history():
    try:
        df = pd.read_csv(HISTORY_FILE)
        return df
    except:
        df = pd.DataFrame(columns=["username","study","sleep","screen","stress","fatigue","burnout"])
        df.to_csv(HISTORY_FILE, index=False)
        return df

# ---------------- USER FUNCTIONS ----------------
def save_user(username, password):
    df = load_users()

    username = username.strip()
    password = password.strip()

    new_user = pd.DataFrame([[username, password]], columns=["username", "password"])
    df = pd.concat([df, new_user], ignore_index=True)
    df.to_csv(USER_FILE, index=False)

def user_exists(username):
    df = load_users()
    username = username.strip()
    df["username"] = df["username"].astype(str).str.strip()
    return username in df["username"].values

def validate_user(username, password):
    df = load_users()

    username = username.strip()
    password = password.strip()

    df["username"] = df["username"].astype(str).str.strip()
    df["password"] = df["password"].astype(str).str.strip()

    user = df[(df["username"] == username) & (df["password"] == password)]
    return not user.empty

# ---------------- SESSION ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "page" not in st.session_state:
    st.session_state.page = "login"

if "current_user" not in st.session_state:
    st.session_state.current_user = None

# ---------------- LOGIN ----------------
def login_page():
    st.title("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if validate_user(username, password):
            st.session_state.logged_in = True
            st.session_state.current_user = username.strip()
            st.success("Login successful")
            st.rerun()
        else:
            st.error("Invalid credentials")

    if st.button("Go to Signup"):
        st.session_state.page = "signup"
        st.rerun()

# ---------------- SIGNUP ----------------
def signup_page():
    st.title("🆕 Signup")

    new_user = st.text_input("Create Username")
    new_pass = st.text_input("Create Password", type="password")

    if st.button("Signup"):
        if user_exists(new_user):
            st.warning("User already exists")
        else:
            save_user(new_user, new_pass)
            st.success("Account created! Please login.")
            st.session_state.page = "login"
            st.rerun()

    if st.button("Back to Login"):
        st.session_state.page = "login"
        st.rerun()

# ---------------- NAVIGATION ----------------
if not st.session_state.logged_in:
    if st.session_state.page == "login":
        login_page()
    else:
        signup_page()
    st.stop()

# ---------------- APP CONFIG ----------------
st.set_page_config(page_title="AI Student Assistant", layout="wide")

st.title("🎓 AI Student Assistant System")
st.write(f"👤 Logged in as: **{st.session_state.current_user}**")

# Logout
if st.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.session_state.page = "login"
    st.rerun()

# ---------------- LOAD MODEL ----------------
model = pickle.load(open("model.pkl", "rb"))

# ---------------- INPUT ----------------
st.subheader("📥 Enter Your Daily Data")

col1, col2 = st.columns(2)

with col1:
    study = st.slider("📘 Study Hours", 0, 12, 6)
    sleep = st.slider("😴 Sleep Hours", 0, 12, 7)
    screen = st.slider("📱 Screen Time", 0, 12, 5)

with col2:
    stress = st.slider("😵 Stress Level", 0, 10, 5)
    fatigue = st.slider("😓 Mental Fatigue", 0, 10, 5)

# ---------------- PDF ----------------
def generate_pdf(result, advice):
    doc = SimpleDocTemplate("report.pdf")
    styles = getSampleStyleSheet()

    content = []
    content.append(Paragraph("AI Student Assistant Report", styles['Title']))
    content.append(Paragraph(f"Result: {result}", styles['Normal']))
    content.append(Paragraph(f"Advice: {advice}", styles['Normal']))

    doc.build(content)

# ---------------- ANALYSIS ----------------
if st.button("🚀 Analyze"):

    features = np.array([[study, sleep, screen, stress, fatigue]])
    prediction = model.predict(features)[0]

    result = "⚠️ High Burnout Risk" if prediction == 1 else "✅ Normal"

    if prediction == 1:
        st.error(result)
    else:
        st.success(result)

    # AI Advice
    st.subheader("🤖 AI Assistant")

    if prediction == 1:
        advice = "⚠️ You are showing signs of burnout.\n\n"

        if sleep < 5:
            advice += "🔴 Very low sleep.\n"
        elif sleep < 6:
            advice += "🟡 Improve sleep.\n"

        if stress >= 8:
            advice += "🔴 High stress.\n"
        elif stress >= 6:
            advice += "🟡 Manage stress.\n"

        if screen >= 8:
            advice += "🔴 Reduce screen time.\n"

        if study >= 9:
            advice += "🟡 Avoid overstudying.\n"

        advice += "\n💡 Take rest and reset routine."
    else:
        advice = """✅ You are doing well!

Maintain:
✔ Good sleep
✔ Balanced study
✔ Low stress"""

    st.write(advice)

    # PDF
    generate_pdf(result, advice)
    with open("report.pdf", "rb") as f:
        st.download_button("📄 Download Report", f, file_name="report.pdf")

    # Graph
    st.subheader("📊 Activity Overview")
    labels = ['Study', 'Sleep', 'Screen', 'Stress', 'Fatigue']
    values = [study, sleep, screen, stress, fatigue]

    fig, ax = plt.subplots()
    ax.bar(labels, values)
    st.pyplot(fig)

    # Save history
    df = load_history()

    new_data = pd.DataFrame([[st.session_state.current_user, study, sleep, screen, stress, fatigue, prediction]],
                            columns=["username","study","sleep","screen","stress","fatigue","burnout"])

    df = pd.concat([df, new_data], ignore_index=True)
    df.to_csv(HISTORY_FILE, index=False)

    st.success("📁 Data saved successfully!")

# ---------------- HISTORY ----------------
if st.checkbox("📂 Show My History"):
    df = load_history()
    user_data = df[df["username"] == st.session_state.current_user]

    if not user_data.empty:
        st.dataframe(user_data)
    else:
        st.warning("No history found for this user.")