import streamlit as st
import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

# Load model
model = pickle.load(open("model.pkl", "rb"))

st.set_page_config(page_title="AI Student Assistant", layout="centered")

st.title("🎓 AI Student Assistant System")

st.subheader("📥 Enter Your Daily Data")

# Inputs
study = st.slider("Study Hours", 0, 12, 6)
sleep = st.slider("Sleep Hours", 0, 12, 7)
screen = st.slider("Screen Time", 0, 12, 5)
stress = st.slider("Stress Level", 0, 10, 5)
fatigue = st.slider("Mental Fatigue", 0, 10, 5)

# Prediction button
if st.button("🚀 Analyze"):

    features = np.array([[study, sleep, screen, stress, fatigue]])
    prediction = model.predict(features)[0]

    # Result
    if prediction == 1:
        st.error("⚠️ High Burnout Risk")
    else:
        st.success("✅ You are doing fine")

    # 🤖 Chatbot Advice
    st.subheader("🤖 AI Assistant Advice")

    advice = ""

    if prediction == 1:
        advice += "You may be experiencing burnout.\n\n"

        if sleep < 6:
            advice += "👉 Improve your sleep schedule\n"
        if stress > 7:
            advice += "👉 Practice stress management (meditation, breaks)\n"
        if screen > 7:
            advice += "👉 Reduce screen time\n"
        if study > 8:
            advice += "👉 Avoid over-studying\n"

        advice += "\n💡 Take care of your mental health!"
    else:
        advice = "You are doing well. Keep maintaining balance 👍"

    st.write(advice)

    # 📊 Graph
    st.subheader("📊 Your Activity Overview")

    labels = ['Study', 'Sleep', 'Screen', 'Stress', 'Fatigue']
    values = [study, sleep, screen, stress, fatigue]

    fig, ax = plt.subplots()
    ax.bar(labels, values)
    st.pyplot(fig)

    # 💾 Save Data
    new_data = pd.DataFrame([[study, sleep, screen, stress, fatigue, prediction]],
                            columns=["study", "sleep", "screen", "stress", "fatigue", "burnout"])

    if os.path.exists("history.csv"):
        new_data.to_csv("history.csv", mode='a', header=False, index=False)
    else:
        new_data.to_csv("history.csv", index=False)

    st.success("📁 Data saved successfully!")

# 📈 Show history
if st.checkbox("📂 Show History"):
    if os.path.exists("history.csv"):
        data = pd.read_csv("history.csv")
        st.dataframe(data)
    else:
        st.warning("No history found yet.")