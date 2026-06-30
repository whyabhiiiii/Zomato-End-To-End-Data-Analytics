"""
============================================================
  Zomato End-to-End Data Analytics
  ML Model 2: Delivery Delay Prediction
  Algorithm: Gradient Boosting Classifier
  Output: delay_model.pkl
============================================================
"""

import pandas as pd
import numpy as np
import os
import pickle
import warnings
warnings.filterwarnings("ignore")

from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (classification_report, roc_auc_score,
                             roc_curve, accuracy_score)
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

print("Loading data for Delivery Delay Model...")
orders   = pd.read_csv(f"{DATA}/orders.csv", parse_dates=["order_date"])
delivery = pd.read_csv(f"{DATA}/delivery.csv")
rests    = pd.read_csv(f"{DATA}/restaurants.csv")

# ─── MERGE ───────────────────────────────────────────────
df = delivery.merge(orders[["order_id","restaurant_id","final_amount","items_count"]],
                    on="order_id")
df = df.merge(rests[["restaurant_id","city","restaurant_type","price_range"]], on="restaurant_id")

le = LabelEncoder()
df["city_enc"] = le.fit_transform(df["city"].astype(str))
df["rest_type_enc"] = le.fit_transform(df["restaurant_type"].astype(str))

# ─── FEATURES ────────────────────────────────────────────
FEATURES = [
    "distance_km",
    "estimated_time_min",
    "is_peak_hour",
    "is_weekend",
    "order_hour",
    "final_amount",
    "items_count",
    "city_enc",
    "rest_type_enc",
    "price_range"
]
df = df.dropna(subset=FEATURES + ["delay_flag"])
X = df[FEATURES]
y = df["delay_flag"]

print(f"\n  Dataset: {len(df):,} deliveries")
print(f"  Delay Rate: {y.mean()*100:.1f}%")

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ─── TRAIN ───────────────────────────────────────────────
print("\nTraining Gradient Boosting Delay Model...")
model = GradientBoostingClassifier(
    n_estimators=200,
    max_depth=5,
    learning_rate=0.1,
    min_samples_split=10,
    random_state=42
)
model.fit(X_train, y_train)

y_pred  = model.predict(X_test)
y_proba = model.predict_proba(X_test)[:, 1]
acc     = accuracy_score(y_test, y_pred)
auc     = roc_auc_score(y_test, y_proba)
cv      = cross_val_score(model, X, y, cv=5, scoring="roc_auc")

print(f"\n{'='*50}")
print(f"  DELAY MODEL RESULTS")
print(f"{'='*50}")
print(f"  Accuracy   : {acc*100:.2f}%")
print(f"  ROC-AUC    : {auc:.4f}")
print(f"  CV AUC     : {cv.mean():.4f} ± {cv.std():.4f}")
print(f"\n{classification_report(y_test, y_pred, target_names=['On Time','Delayed'])}")

# ─── SAVE ────────────────────────────────────────────────
with open(f"{OUT}/delay_model.pkl", "wb") as f:
    pickle.dump({"model": model, "features": FEATURES,
                 "le_city": le, "acc": acc, "auc": auc}, f)
print(f"✅ Model saved → Models/delay_model.pkl")

# Feature importance CSV
fi = pd.DataFrame({"feature": FEATURES, "importance": model.feature_importances_})
fi = fi.sort_values("importance", ascending=False)
fi.to_csv(f"{OUT}/delay_feature_importance.csv", index=False)

# ─── VISUALISATIONS ──────────────────────────────────────
# Feature importance
fig, ax = plt.subplots(figsize=(9, 6))
clrs = [ZOMATO_RED if i < 3 else ACCENT if i < 6 else "#666" for i in range(len(fi))]
ax.barh(fi["feature"][::-1], fi["importance"][::-1], color=clrs[::-1])
ax.set_title(f"🚴 Delay Model — Feature Importance  (AUC={auc:.3f})")
ax.set_xlabel("Importance Score")
ax.grid(axis="x"); ax.set_axisbelow(True)
fig.savefig(f"{VIZ}/14_delay_feature_importance.png", bbox_inches="tight", facecolor=ZOMATO_DARK)
plt.close()

# ROC Curve
fpr, tpr, _ = roc_curve(y_test, y_proba)
fig, ax = plt.subplots(figsize=(7, 6))
ax.plot(fpr, tpr, color=ACCENT, lw=2.5, label=f"Delay Model (AUC = {auc:.3f})")
ax.plot([0,1],[0,1], "--", color="#555")
ax.fill_between(fpr, tpr, alpha=0.15, color=ACCENT)
ax.set_xlabel("False Positive Rate"); ax.set_ylabel("True Positive Rate")
ax.set_title("📊 ROC Curve — Delivery Delay Prediction")
ax.legend(framealpha=0.2); ax.grid()
fig.savefig(f"{VIZ}/15_delay_roc_curve.png", bbox_inches="tight", facecolor=ZOMATO_DARK)
plt.close()

print(f"💾 Visualisations saved.")
print(f"🎉 Phase 4b (Delay Model) Complete!\n")
