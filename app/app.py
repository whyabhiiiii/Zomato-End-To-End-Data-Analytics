"""
============================================================
  Zomato End-to-End Data Analytics — Flask Web Application
  3 Prediction Tools + Analytics Dashboard
  Run: python3 app.py
============================================================
"""

from flask import Flask, render_template, request, jsonify
import pickle
import os
import pandas as pd
import numpy as np

app = Flask(__name__)

BASE    = os.path.dirname(os.path.abspath(__file__))
MODELS  = os.path.join(BASE, "..", "Models")

# ─── LOAD MODELS ─────────────────────────────────────────
def load_model(fname):
    path = os.path.join(MODELS, fname)
    if os.path.exists(path):
        with open(path, "rb") as f:
            return pickle.load(f)
    return None

churn_bundle  = load_model("churn_model.pkl")
delay_bundle  = load_model("delay_model.pkl")
rating_bundle = load_model("rating_model.pkl")

print(f"✅ Churn model  : {'loaded' if churn_bundle else 'not found'}")
print(f"✅ Delay model  : {'loaded' if delay_bundle else 'not found'}")
print(f"✅ Rating model : {'loaded' if rating_bundle else 'not found'}")

# ─── ROUTES ──────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/churn")
def churn_page():
    return render_template("churn.html")

@app.route("/delay")
def delay_page():
    return render_template("delay.html")

@app.route("/rating")
def rating_page():
    return render_template("rating.html")

# ─── PREDICT CHURN ───────────────────────────────────────
@app.route("/predict/churn", methods=["POST"])
def predict_churn():
    try:
        d = request.get_json()
        features = churn_bundle["features"]
        vals = []
        for f in features:
            vals.append(float(d.get(f, 0)))
        X = np.array(vals).reshape(1, -1)
        model = churn_bundle["model"]
        prob  = model.predict_proba(X)[0][1]
        pred  = int(prob > 0.5)

        risk = "Critical 🔴" if prob > 0.8 else "High 🟠" if prob > 0.6 else "Medium 🟡" if prob > 0.3 else "Low 🟢"
        msg  = (
            "This customer is very likely to churn. Immediate retention action recommended."
            if prob > 0.6 else
            "Moderate churn risk. Consider a discount coupon or push notification."
            if prob > 0.3 else
            "Customer is engaged and unlikely to churn. Keep up the service quality!"
        )
        return jsonify({
            "probability": round(float(prob) * 100, 1),
            "prediction": pred,
            "risk_level": risk,
            "message": msg
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# ─── PREDICT DELAY ───────────────────────────────────────
@app.route("/predict/delay", methods=["POST"])
def predict_delay():
    try:
        d = request.get_json()
        features = delay_bundle["features"]
        vals = []
        for f in features:
            vals.append(float(d.get(f, 0)))
        X = np.array(vals).reshape(1, -1)
        model = delay_bundle["model"]
        prob  = model.predict_proba(X)[0][1]
        pred  = int(prob > 0.5)

        msg = (
            "⚠️ High chance of delivery delay. Consider alerting the customer proactively."
            if pred == 1 else
            "✅ Delivery likely to be on time based on current conditions."
        )
        return jsonify({
            "probability": round(float(prob) * 100, 1),
            "prediction": pred,
            "label": "Likely Delayed" if pred else "On Time",
            "message": msg
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# ─── PREDICT RATING ──────────────────────────────────────
@app.route("/predict/rating", methods=["POST"])
def predict_rating():
    try:
        d = request.get_json()
        features = rating_bundle["features"]
        vals = []
        for f in features:
            vals.append(float(d.get(f, 0)))
        X = np.array(vals).reshape(1, -1)
        model = rating_bundle["model"]
        pred  = model.predict(X)[0]
        pred  = max(1.0, min(5.0, float(pred)))

        stars = "⭐⭐⭐⭐⭐" if pred >= 4.5 else "⭐⭐⭐⭐" if pred >= 3.5 else "⭐⭐⭐" if pred >= 2.5 else "⭐⭐"
        msg = (
            "Excellent! This restaurant is predicted to be top-rated." if pred >= 4.0 else
            "Good restaurant with solid performance." if pred >= 3.0 else
            "Below average. Focus on quality and delivery improvements."
        )
        return jsonify({
            "predicted_rating": round(pred, 2),
            "stars": stars,
            "message": msg
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# ─── KPI API ─────────────────────────────────────────────
@app.route("/api/kpis")
def kpis():
    try:
        DATA = os.path.join(BASE, "..", "Data")
        orders = pd.read_csv(f"{DATA}/orders.csv")
        delivery = pd.read_csv(f"{DATA}/delivery.csv")
        delivered = orders[orders["order_status"] == "Delivered"]
        return jsonify({
            "total_revenue":   f"₹{delivered['final_amount'].sum():,.0f}",
            "total_orders":    f"{len(orders):,}",
            "aov":             f"₹{delivered['final_amount'].mean():.2f}",
            "active_users":    f"{orders['user_id'].nunique():,}",
            "delay_rate":      f"{delivery['delay_flag'].mean()*100:.1f}%",
            "cancellation_pct":f"{(orders['order_status']=='Cancelled').mean()*100:.1f}%"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("\n🍕 Zomato Analytics App starting...")
    print("   Open: http://localhost:8080\n")
    app.run(debug=True, port=8080)
