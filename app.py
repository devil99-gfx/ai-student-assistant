from flask import Flask, request, render_template
import pickle
import numpy as np

# CREATE APP FIRST
app = Flask(__name__)

# LOAD MODEL
model = pickle.load(open("model.pkl", "rb"))

# HOME ROUTE
@app.route('/')
def home():
    return render_template('index.html')

# CHATBOT FUNCTION
def get_advice(prediction, study, sleep, screen, stress, fatigue):
    if prediction == 1:
        advice = "⚠️ You may be experiencing burnout.\n"
        
        if sleep < 6:
            advice += "👉 Improve your sleep schedule.\n"
        if stress > 7:
            advice += "👉 Try stress management.\n"
        if screen > 7:
            advice += "👉 Reduce screen time.\n"
        if study > 8:
            advice += "👉 Avoid over-studying.\n"
        
        advice += "💡 Take care of your mental health!"
    else:
        advice = "✅ You are doing well. Keep balance!"

    return advice

# PREDICT ROUTE
@app.route('/predict', methods=['POST'])
def predict():
    study = float(request.form['study_hours'])
    sleep = float(request.form['sleep_hours'])
    screen = float(request.form['screen_time'])
    stress = float(request.form['stress_level'])
    fatigue = float(request.form['mental_fatigue'])

    features = np.array([[study, sleep, screen, stress, fatigue]])
    prediction = model.predict(features)[0]

    result = "⚠️ High Burnout Risk" if prediction == 1 else "✅ Normal"
    chatbot_response = get_advice(prediction, study, sleep, screen, stress, fatigue)

    return render_template(
        'index.html',
        prediction_text=result,
        chatbot_text=chatbot_response
    )

# RUN APP
if __name__ == "__main__":
    app.run(debug=True)