"""
============================================================
  Zomato End-to-End Data Analytics
  ML Model 1: Customer Churn Prediction (RFM-based)
  Algorithm: Random Forest Classifier
  Output: churn_model.pkl + feature_importance.csv
============================================================
"""

import pandas as pd
import numpy as np
import os
import pickle
import warnings
warnings.filterwarnings("ignore")

from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import (classification_report, confusion_matrix,
                             roc_auc_score, roc_curve, accuracy_score)
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

# ─── PATHS ───────────────────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "..", "Data")
OUT  = os.path.join(BASE, "..", "Models")
VIZ  = os.path.join(BASE, "..", "Dashboard", "Dashboard_Screenshots")
os.makedirs(OUT, exist_ok=True)
os.makedirs(VIZ, exist_ok=True)

ZOMATO_RED  = "#E23744"
ZOMATO_DARK = "#1C1C1C"
ACCENT      = "#FF6B35"

plt.rcParams.update({
    "figure.facecolor": ZOMATO_DARK, "axes.facecolor": "#2A2A2A",
    "axes.edgecolor": "#444", "axes.labelcolor": "white",
    "xtick.color": "#CCCCCC", "ytick.color": "#CCCCCC",
    "text.color": "white", "grid.color": "#444",
    "grid.linestyle": "--", "grid.alpha": 0.4,
})

# ─── LOAD DATA ───────────────────────────────────────────
print("Loading data...")
orders  = pd.read_csv(f"{DATA}/orders.csv",  parse_dates=["order_date"])
users   = pd.read_csv(f"{DATA}/users.csv")
delivery= pd.read_csv(f"{DATA}/delivery.csv")
reviews = pd.read_csv(f"{DATA}/reviews.csv")

delivered = orders[orders["order_status"] == "Delivered"].copy()
print(f"✅ Delivered orders: {len(delivered):,}")

# ─── FEATURE ENGINEERING ─────────────────────────────────
ref_date = delivered["order_date"].max()

rfm = delivered.groupby("user_id").agg(
    recency=("order_date", lambda x: (ref_date - x.max()).days),
    frequency=("order_id", "count"),
    monetary=("final_amount", "sum"),
    avg_order_value=("final_amount", "mean"),
    avg_discount=("discount_amount", "mean"),
    last_order_date=("order_date", "max"),
).reset_index()

# Review features
rev_feat = reviews.groupby("user_id").agg(
    avg_rating=("rating", "mean"),
    review_count=("review_id", "count"),
    neg_reviews=("sentiment", lambda x: (x == "Negative").sum())
).reset_index()

# Delivery experience
del_feat = (
    delivery.merge(orders[["order_id","user_id"]], on="order_id")
    .groupby("user_id").agg(
        avg_delivery_time=("actual_time_min", "mean"),
        delay_count=("delay_flag", "sum"),
        total_deliveries=("delivery_id", "count")
    ).reset_index()
)
del_feat["delay_rate"] = del_feat["delay_count"] / del_feat["total_deliveries"]

# User demographics
user_feat = users[["user_id","age","gender","is_gold_member","marital_status","occupation"]].copy()
le = LabelEncoder()
user_feat["gender_enc"]      = le.fit_transform(user_feat["gender"].astype(str))
user_feat["marital_enc"]     = le.fit_transform(user_feat["marital_status"].astype(str))
user_feat["occupation_enc"]  = le.fit_transform(user_feat["occupation"].astype(str))

# ─── MERGE ALL FEATURES ──────────────────────────────────
df = rfm.merge(rev_feat, on="user_id", how="left")
df = df.merge(del_feat[["user_id","avg_delivery_time","delay_rate"]], on="user_id", how="left")
df = df.merge(user_feat[["user_id","age","gender_enc","is_gold_member","marital_enc","occupation_enc"]],
              on="user_id", how="left")
df.fillna(df.median(numeric_only=True), inplace=True)

# ─── CHURN LABEL ─────────────────────────────────────────
# Churned = no order in last 90 days
df["churned"] = (df["recency"] > 90).astype(int)
print(f"\n  Churn Distribution:")
print(df["churned"].value_counts())
print(f"  Churn Rate: {df['churned'].mean()*100:.1f}%\n")

# ─── FEATURES & TARGET ───────────────────────────────────
FEATURES = [
    "recency","frequency","monetary","avg_order_value","avg_discount",
    "avg_rating","review_count","neg_reviews",
    "avg_delivery_time","delay_rate",
    "age","gender_enc","is_gold_member","marital_enc","occupation_enc"
]
X = df[FEATURES]
y = df["churned"]

# ─── TRAIN / TEST SPLIT ──────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ─── MODEL TRAINING ──────────────────────────────────────
print("Training Random Forest Churn Model...")
model = RandomForestClassifier(
    n_estimators=300,
    max_depth=12,
    min_samples_split=5,
    min_samples_leaf=2,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1
)
model.fit(X_train, y_train)

# ─── EVALUATION ──────────────────────────────────────────
y_pred  = model.predict(X_test)
y_proba = model.predict_proba(X_test)[:, 1]
acc     = accuracy_score(y_test, y_pred)
auc     = roc_auc_score(y_test, y_proba)

cv_scores = cross_val_score(model, X, y, cv=StratifiedKFold(5), scoring="roc_auc")

print(f"\n{'='*50}")
print(f"  CHURN MODEL RESULTS")
print(f"{'='*50}")
print(f"  Accuracy   : {acc*100:.2f}%")
print(f"  ROC-AUC    : {auc:.4f}")
print(f"  CV AUC     : {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
print(f"\n{classification_report(y_test, y_pred, target_names=['Active','Churned'])}")

# ─── SAVE MODEL ──────────────────────────────────────────
with open(f"{OUT}/churn_model.pkl", "wb") as f:
    pickle.dump({"model": model, "features": FEATURES, "acc": acc, "auc": auc}, f)
print(f"✅ Model saved → Models/churn_model.pkl")

# Feature importance CSV
fi = pd.DataFrame({"feature": FEATURES, "importance": model.feature_importances_})
fi = fi.sort_values("importance", ascending=False)
fi.to_csv(f"{OUT}/churn_feature_importance.csv", index=False)

# ─── VISUALISATIONS ──────────────────────────────────────
# 1. Feature Importance
fig, ax = plt.subplots(figsize=(10, 7))
colors = [ZOMATO_RED if i < 3 else ACCENT if i < 7 else "#666" for i in range(len(fi))]
ax.barh(fi["feature"][::-1], fi["importance"][::-1], color=colors[::-1])
ax.set_title(f"🔍 Churn Model — Feature Importance  (AUC={auc:.3f})")
ax.set_xlabel("Importance Score")
ax.grid(axis="x"); ax.set_axisbelow(True)
fig.savefig(f"{VIZ}/11_churn_feature_importance.png", bbox_inches="tight", facecolor=ZOMATO_DARK)
plt.close()

# 2. ROC Curve
fpr, tpr, _ = roc_curve(y_test, y_proba)
fig, ax = plt.subplots(figsize=(7, 6))
ax.plot(fpr, tpr, color=ZOMATO_RED, lw=2.5, label=f"Churn Model (AUC = {auc:.3f})")
ax.plot([0,1],[0,1], "--", color="#555", label="Random Baseline")
ax.fill_between(fpr, tpr, alpha=0.15, color=ZOMATO_RED)
ax.set_xlabel("False Positive Rate"); ax.set_ylabel("True Positive Rate")
ax.set_title("📊 ROC Curve — Churn Prediction")
ax.legend(framealpha=0.2); ax.grid()
fig.savefig(f"{VIZ}/12_churn_roc_curve.png", bbox_inches="tight", facecolor=ZOMATO_DARK)
plt.close()

# 3. Churn Risk Distribution
churn_proba = model.predict_proba(X)[:,1]
df["churn_probability"] = churn_proba
df["risk_tier"] = pd.cut(churn_proba, bins=[0,.3,.6,.8,1],
                          labels=["Low Risk","Medium Risk","High Risk","Critical"])

risk_counts = df["risk_tier"].value_counts()
fig, ax = plt.subplots(figsize=(8, 5))
colors_r = ["#4CAF50", ACCENT, ZOMATO_RED, "#8B0000"]
ax.bar(risk_counts.index, risk_counts.values, color=colors_r, edgecolor="none")
for i, v in enumerate(risk_counts.values):
    ax.text(i, v+50, f"{v:,}", ha="center", fontsize=10)
ax.set_title("⚠️ Customer Churn Risk Distribution")
ax.set_ylabel("Number of Customers")
ax.grid(axis="y"); ax.set_axisbelow(True)
fig.savefig(f"{VIZ}/13_churn_risk_tiers.png", bbox_inches="tight", facecolor=ZOMATO_DARK)
plt.close()

print(f"\n💾 Visualisations saved to Dashboard_Screenshots/")
print(f"🎉 Phase 4a (Churn Model) Complete!\n")
