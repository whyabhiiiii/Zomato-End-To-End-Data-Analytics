"""
============================================================
  Zomato End-to-End Data Analytics
  ML Model 3: Restaurant Rating Predictor
  Algorithm: Random Forest Regressor
  Output: rating_model.pkl
============================================================
"""

import pandas as pd
import numpy as np
import os
import pickle
import warnings
warnings.filterwarnings("ignore")

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error
import matplotlib.pyplot as plt

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "..", "Data")
OUT  = os.path.join(BASE, "..", "Models")
VIZ  = os.path.join(BASE, "..", "Dashboard", "Dashboard_Screenshots")

ZOMATO_RED = "#E23744"; ZOMATO_DARK = "#1C1C1C"; ACCENT = "#FF6B35"
plt.rcParams.update({
    "figure.facecolor": ZOMATO_DARK, "axes.facecolor": "#2A2A2A",
    "axes.edgecolor": "#444", "axes.labelcolor": "white",
    "xtick.color": "#CCCCCC", "ytick.color": "#CCCCCC",
    "text.color": "white", "grid.color": "#444", "grid.linestyle": "--",
})

print("Loading data for Rating Prediction Model...")
rests    = pd.read_csv(f"{DATA}/restaurants.csv")
orders   = pd.read_csv(f"{DATA}/orders.csv", parse_dates=["order_date"])
reviews  = pd.read_csv(f"{DATA}/reviews.csv")
delivery = pd.read_csv(f"{DATA}/delivery.csv")

# ─── RESTAURANT LEVEL FEATURES ───────────────────────────
rev_feat = orders[orders["order_status"]=="Delivered"].groupby("restaurant_id").agg(
    total_orders=("order_id","count"),
    total_revenue=("final_amount","sum"),
    avg_order_value=("final_amount","mean"),
    avg_discount=("discount_amount","mean")
).reset_index()

sent_feat = reviews.groupby("restaurant_id").agg(
    total_reviews=("review_id","count"),
    avg_review_rating=("rating","mean"),
    pos_reviews=("sentiment", lambda x: (x=="Positive").sum()),
    neg_reviews=("sentiment", lambda x: (x=="Negative").sum())
).reset_index()
sent_feat["pos_pct"] = sent_feat["pos_reviews"] / sent_feat["total_reviews"] * 100

del_feat = (
    delivery.merge(orders[["order_id","restaurant_id"]], on="order_id")
    .groupby("restaurant_id").agg(
        avg_delivery_time=("actual_time_min","mean"),
        delay_rate=("delay_flag","mean"),
        avg_distance=("distance_km","mean")
    ).reset_index()
)

df = rests.merge(rev_feat, on="restaurant_id", how="left")
df = df.merge(sent_feat, on="restaurant_id", how="left")
df = df.merge(del_feat,  on="restaurant_id", how="left")
df.fillna(df.median(numeric_only=True), inplace=True)

le = LabelEncoder()
df["city_enc"]        = le.fit_transform(df["city"].astype(str))
df["cuisine_enc"]     = le.fit_transform(df["cuisine"].astype(str))
df["rest_type_enc"]   = le.fit_transform(df["restaurant_type"].astype(str))

FEATURES = [
    "price_range", "avg_cost_for_two", "online_delivery", "table_booking",
    "total_orders", "total_revenue", "avg_order_value", "avg_discount",
    "total_reviews", "avg_review_rating", "pos_pct", "neg_reviews",
    "avg_delivery_time", "delay_rate", "avg_distance",
    "city_enc", "cuisine_enc", "rest_type_enc", "opening_year"
]

TARGET = "rating"
df = df.dropna(subset=[TARGET] + FEATURES)
X = df[FEATURES]
y = df[TARGET]

print(f"\n  Dataset: {len(df):,} restaurants")
print(f"  Rating range: {y.min():.1f} – {y.max():.1f}")

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ─── TRAIN ───────────────────────────────────────────────
print("\nTraining Random Forest Rating Model...")
model = RandomForestRegressor(
    n_estimators=300,
    max_depth=10,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1
)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
mae    = mean_absolute_error(y_test, y_pred)
r2     = r2_score(y_test, y_pred)
rmse   = mean_squared_error(y_test, y_pred) ** 0.5
cv     = cross_val_score(model, X, y, cv=5, scoring="r2")

print(f"\n{'='*50}")
print(f"  RATING MODEL RESULTS")
print(f"{'='*50}")
print(f"  MAE      : {mae:.4f} stars")
print(f"  RMSE     : {rmse:.4f} stars")
print(f"  R²       : {r2:.4f}")
print(f"  CV R²    : {cv.mean():.4f} ± {cv.std():.4f}")

# ─── SAVE ────────────────────────────────────────────────
with open(f"{OUT}/rating_model.pkl", "wb") as f:
    pickle.dump({"model": model, "features": FEATURES,
                 "mae": mae, "r2": r2, "rmse": rmse}, f)
print(f"✅ Model saved → Models/rating_model.pkl")

fi = pd.DataFrame({"feature": FEATURES, "importance": model.feature_importances_})
fi = fi.sort_values("importance", ascending=False)
fi.to_csv(f"{OUT}/rating_feature_importance.csv", index=False)

# ─── VISUALISATIONS ──────────────────────────────────────
# Feature importance
fig, ax = plt.subplots(figsize=(10, 7))
clrs = [ZOMATO_RED if i < 3 else ACCENT if i < 8 else "#666" for i in range(len(fi))]
ax.barh(fi["feature"][::-1], fi["importance"][::-1], color=clrs[::-1])
ax.set_title(f"⭐ Rating Model — Feature Importance  (R²={r2:.3f})")
ax.set_xlabel("Importance Score")
ax.grid(axis="x"); ax.set_axisbelow(True)
fig.savefig(f"{VIZ}/16_rating_feature_importance.png", bbox_inches="tight", facecolor=ZOMATO_DARK)
plt.close()

# Predicted vs Actual
fig, ax = plt.subplots(figsize=(7, 6))
ax.scatter(y_test, y_pred, alpha=0.4, color=ACCENT, s=12, label="Predictions")
ax.plot([y.min(), y.max()], [y.min(), y.max()], "--", color=ZOMATO_RED, lw=2, label="Perfect Fit")
ax.set_xlabel("Actual Rating"); ax.set_ylabel("Predicted Rating")
ax.set_title(f"📊 Rating: Predicted vs Actual  (MAE={mae:.3f})")
ax.legend(framealpha=0.2); ax.grid()
fig.savefig(f"{VIZ}/17_rating_predicted_vs_actual.png", bbox_inches="tight", facecolor=ZOMATO_DARK)
plt.close()

print(f"💾 Visualisations saved.")
print(f"🎉 Phase 4c (Rating Model) Complete!\n")
