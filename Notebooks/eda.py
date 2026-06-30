"""
============================================================
  Zomato End-to-End Data Analytics
  Exploratory Data Analysis (EDA) Notebook
  Run: jupyter notebook or just python3 eda.py
============================================================
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import warnings
import os

warnings.filterwarnings("ignore")

# ─── PATHS ───────────────────────────────────────────────
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "Data")
OUT_DIR  = os.path.join(os.path.dirname(__file__), "..", "Dashboard", "Dashboard_Screenshots")
os.makedirs(OUT_DIR, exist_ok=True)

# ─── STYLE ───────────────────────────────────────────────
ZOMATO_RED  = "#E23744"
ZOMATO_DARK = "#1C1C1C"
ZOMATO_GRAY = "#F5F5F5"
ACCENT      = "#FF6B35"

plt.rcParams.update({
    "figure.facecolor":  ZOMATO_DARK,
    "axes.facecolor":    "#2A2A2A",
    "axes.edgecolor":    "#444",
    "axes.labelcolor":   "white",
    "xtick.color":       "#CCCCCC",
    "ytick.color":       "#CCCCCC",
    "text.color":        "white",
    "grid.color":        "#444",
    "grid.linestyle":    "--",
    "grid.alpha":        0.4,
    "font.family":       "DejaVu Sans",
    "axes.titlesize":    13,
    "axes.titleweight":  "bold",
    "figure.dpi":        120,
})

# ─── LOAD DATA ───────────────────────────────────────────
print("Loading datasets...")
users   = pd.read_csv(f"{DATA_DIR}/users.csv")
rests   = pd.read_csv(f"{DATA_DIR}/restaurants.csv")
menu    = pd.read_csv(f"{DATA_DIR}/menu.csv")
orders  = pd.read_csv(f"{DATA_DIR}/orders.csv",  parse_dates=["order_date"])
reviews = pd.read_csv(f"{DATA_DIR}/reviews.csv", parse_dates=["review_date"])
delivery= pd.read_csv(f"{DATA_DIR}/delivery.csv",parse_dates=["order_date"])

print(f"✅ Users: {len(users):,}  |  Restaurants: {len(rests):,}  |  Menu: {len(menu):,}")
print(f"   Orders: {len(orders):,}  |  Reviews: {len(reviews):,}  |  Delivery: {len(delivery):,}")

# ─── 1. KPI SUMMARY ─────────────────────────────────────
delivered = orders[orders["order_status"] == "Delivered"]
total_rev  = delivered["final_amount"].sum()
total_ord  = len(orders)
aov        = delivered["final_amount"].mean()
active_usr = orders["user_id"].nunique()
delay_rate = delivery["delay_flag"].mean() * 100

print(f"\n{'='*50}")
print(f"  ZOMATO ANALYTICS — KPI SUMMARY")
print(f"{'='*50}")
print(f"  Total Revenue    : ₹{total_rev:,.0f}")
print(f"  Total Orders     : {total_ord:,}")
print(f"  Avg Order Value  : ₹{aov:.2f}")
print(f"  Active Users     : {active_usr:,}")
print(f"  Delay Rate       : {delay_rate:.1f}%")
print(f"{'='*50}\n")

# ─── HELPER ──────────────────────────────────────────────
def save(fig, name):
    path = f"{OUT_DIR}/{name}.png"
    fig.savefig(path, bbox_inches="tight", facecolor=ZOMATO_DARK)
    plt.close(fig)
    print(f"  💾 Saved → {name}.png")


# ══════════════════════════════════════════════════════════
# CHART 1: Top 10 Restaurants by Revenue
# ══════════════════════════════════════════════════════════
rev_by_rest = (
    delivered.merge(rests[["restaurant_id","name"]], on="restaurant_id")
    .groupby("name")["final_amount"].sum()
    .nlargest(10).sort_values()
)
fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.barh(rev_by_rest.index, rev_by_rest.values, color=ZOMATO_RED, edgecolor="none")
for bar in bars:
    ax.text(bar.get_width() + 50000, bar.get_y() + bar.get_height()/2,
            f"₹{bar.get_width()/1e6:.1f}M", va="center", fontsize=9, color="#CCCCCC")
ax.set_xlabel("Revenue (₹)")
ax.set_title("🏆 Top 10 Restaurants by Revenue")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x/1e6:.1f}M"))
ax.grid(axis="x"); ax.set_axisbelow(True)
save(fig, "01_top_restaurants_revenue")

# ══════════════════════════════════════════════════════════
# CHART 2: Revenue by Cuisine
# ══════════════════════════════════════════════════════════
rev_cuisine = (
    delivered.merge(rests[["restaurant_id","cuisine"]], on="restaurant_id")
    .groupby("cuisine")["final_amount"].sum().sort_values(ascending=False)
)
colors_cuisine = [ZOMATO_RED if i == 0 else ACCENT if i == 1 else "#888" for i in range(len(rev_cuisine))]
fig, ax = plt.subplots(figsize=(12, 5))
ax.bar(rev_cuisine.index, rev_cuisine.values, color=colors_cuisine, edgecolor="none")
ax.set_title("🍽️  Revenue by Cuisine Type")
ax.set_ylabel("Revenue (₹)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x/1e6:.1f}M"))
plt.xticks(rotation=35, ha="right")
ax.grid(axis="y"); ax.set_axisbelow(True)
save(fig, "02_revenue_by_cuisine")

# ══════════════════════════════════════════════════════════
# CHART 3: Monthly Revenue Trend
# ══════════════════════════════════════════════════════════
monthly = (
    delivered.set_index("order_date")
    .resample("ME")["final_amount"].sum()
)
fig, ax = plt.subplots(figsize=(14, 5))
ax.fill_between(monthly.index, monthly.values, alpha=0.3, color=ZOMATO_RED)
ax.plot(monthly.index, monthly.values, color=ZOMATO_RED, linewidth=2.5, marker="o", markersize=4)
ax.set_title("📈 Monthly Revenue Trend")
ax.set_ylabel("Revenue (₹)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x/1e6:.1f}M"))
ax.grid(); ax.set_axisbelow(True)
save(fig, "03_monthly_revenue_trend")

# ══════════════════════════════════════════════════════════
# CHART 4: Orders by Hour (Peak Hour Heatmap)
# ══════════════════════════════════════════════════════════
orders["order_hour"] = pd.to_datetime(orders["order_time"], format="%H:%M:%S", errors="coerce").dt.hour
hourly = orders.groupby("order_hour").size().reset_index(name="orders")
fig, ax = plt.subplots(figsize=(14, 4))
bar_colors = [ZOMATO_RED if h in [12,13,19,20,21] else ACCENT if h in [11,14,18,22] else "#555"
              for h in hourly["order_hour"]]
ax.bar(hourly["order_hour"], hourly["orders"], color=bar_colors, width=0.8)
ax.set_xticks(range(24)); ax.set_xlabel("Hour of Day")
ax.set_ylabel("Number of Orders")
ax.set_title("⏰ Order Volume by Hour of Day (Peak Hours in Red)")
ax.grid(axis="y"); ax.set_axisbelow(True)
save(fig, "04_peak_hour_analysis")

# ══════════════════════════════════════════════════════════
# CHART 5: Gold vs Regular Member Comparison
# ══════════════════════════════════════════════════════════
merged = delivered.merge(users[["user_id","is_gold_member"]], on="user_id")
gold_comp = merged.groupby("is_gold_member").agg(
    avg_order_value=("final_amount","mean"),
    avg_discount=("discount_amount","mean"),
    total_orders=("order_id","count")
).reset_index()
gold_comp["member_type"] = gold_comp["is_gold_member"].map({0:"Regular",1:"Gold Member"})

fig, axes = plt.subplots(1, 3, figsize=(14, 5))
metrics = [("avg_order_value","Avg Order Value (₹)","💛"),
           ("avg_discount","Avg Discount (₹)","🏷️"),
           ("total_orders","Total Orders","📦")]
bar_clrs = ["#888888", "#FFD700"]

for ax, (col, label, icon) in zip(axes, metrics):
    bars = ax.bar(gold_comp["member_type"], gold_comp[col], color=bar_clrs, width=0.5, edgecolor="none")
    ax.set_title(f"{icon} {label}")
    for b in bars:
        ax.text(b.get_x()+b.get_width()/2, b.get_height()+5, f"{b.get_height():,.0f}",
                ha="center", va="bottom", fontsize=10)
    ax.grid(axis="y"); ax.set_axisbelow(True)

fig.suptitle("💛 Gold Members vs Regular Members", fontsize=15, y=1.02)
plt.tight_layout()
save(fig, "05_gold_vs_regular")

# ══════════════════════════════════════════════════════════
# CHART 6: RFM Segment Distribution
# ══════════════════════════════════════════════════════════
rfm = (
    delivered.groupby("user_id").agg(
        recency=("order_date", lambda x: (delivered["order_date"].max() - x.max()).days),
        frequency=("order_id","count"),
        monetary=("final_amount","sum")
    ).reset_index()
)
rfm["r_score"] = pd.qcut(rfm["recency"].rank(method="first"), 5, labels=[5,4,3,2,1]).astype(int)
rfm["f_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels=[1,2,3,4,5]).astype(int)
rfm["m_score"] = pd.qcut(rfm["monetary"].rank(method="first"), 5, labels=[1,2,3,4,5]).astype(int)

def rfm_label(row):
    r, f = row["r_score"], row["f_score"]
    if r >= 4 and f >= 4: return "Champions"
    elif r >= 3 and f >= 3: return "Loyal Customers"
    elif r >= 4 and f < 2: return "New Customers"
    elif 2 <= r <= 3 and f >= 3: return "Potential Loyalists"
    elif r < 2 and f >= 3: return "At Risk"
    elif r < 2 and f < 2: return "Lost"
    return "Needs Attention"

rfm["segment"] = rfm.apply(rfm_label, axis=1)
seg_counts = rfm["segment"].value_counts()

seg_colors = {
    "Champions": "#FFD700", "Loyal Customers": ZOMATO_RED, "Potential Loyalists": ACCENT,
    "New Customers": "#4CAF50", "Needs Attention": "#9C27B0",
    "At Risk": "#FF5722", "Lost": "#607D8B"
}
colors_pie = [seg_colors.get(s, "#888") for s in seg_counts.index]

fig, ax = plt.subplots(figsize=(10, 7))
wedges, texts, autotexts = ax.pie(
    seg_counts.values, labels=seg_counts.index,
    autopct="%1.1f%%", colors=colors_pie,
    pctdistance=0.82, startangle=140,
    wedgeprops=dict(linewidth=1.5, edgecolor=ZOMATO_DARK)
)
for t in autotexts: t.set_color("white"); t.set_fontsize(9)
ax.set_title("🎯 RFM Customer Segmentation", fontsize=15, pad=20)
save(fig, "06_rfm_segmentation")

# ══════════════════════════════════════════════════════════
# CHART 7: Delay Rate by City
# ══════════════════════════════════════════════════════════
city_delay = (
    delivery.merge(orders[["order_id","restaurant_id"]], on="order_id")
    .merge(rests[["restaurant_id","city"]], on="restaurant_id")
    .groupby("city")["delay_flag"].mean().mul(100).sort_values(ascending=False)
    .reset_index()
)
city_delay.columns = ["city","delay_rate"]

fig, ax = plt.subplots(figsize=(10, 5))
bar_c = [ZOMATO_RED if v > 30 else ACCENT if v > 20 else "#4CAF50" for v in city_delay["delay_rate"]]
ax.bar(city_delay["city"], city_delay["delay_rate"], color=bar_c, edgecolor="none")
for i, (c, v) in city_delay.iterrows():
    ax.text(i, v + 0.3, f"{v:.1f}%", ha="center", fontsize=9, color="white")
ax.set_ylabel("Delay Rate (%)")
ax.set_title("🚴 Delivery Delay Rate by City")
ax.grid(axis="y"); ax.set_axisbelow(True)
save(fig, "07_delay_rate_by_city")

# ══════════════════════════════════════════════════════════
# CHART 8: Sentiment Distribution by City
# ══════════════════════════════════════════════════════════
sent_city = (
    reviews.merge(rests[["restaurant_id","city"]], on="restaurant_id")
    .groupby(["city","sentiment"]).size().unstack(fill_value=0)
)
sent_city_pct = sent_city.div(sent_city.sum(axis=1), axis=0) * 100

fig, ax = plt.subplots(figsize=(12, 6))
sent_city_pct.plot(kind="bar", ax=ax, color=["#4CAF50","#9E9E9E",ZOMATO_RED],
                   edgecolor="none", width=0.7)
ax.set_title("⭐ Review Sentiment Distribution by City")
ax.set_ylabel("Percentage (%)")
ax.set_xlabel("")
plt.xticks(rotation=30, ha="right")
ax.legend(title="Sentiment", framealpha=0.2)
ax.grid(axis="y"); ax.set_axisbelow(True)
save(fig, "08_sentiment_by_city")

# ══════════════════════════════════════════════════════════
# CHART 9: Revenue by City (Map-style bar)
# ══════════════════════════════════════════════════════════
city_rev = (
    delivered.merge(rests[["restaurant_id","city"]], on="restaurant_id")
    .groupby("city")["final_amount"].sum().sort_values(ascending=False)
)
fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.bar(city_rev.index, city_rev.values,
              color=[ZOMATO_RED, ACCENT] + ["#555"]*(len(city_rev)-2), edgecolor="none")
for bar in bars:
    ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+100000,
            f"₹{bar.get_height()/1e6:.1f}M", ha="center", fontsize=9, color="#CCCCCC")
ax.set_title("🏙️  Revenue by City")
ax.set_ylabel("Revenue (₹)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x/1e6:.0f}M"))
ax.grid(axis="y"); ax.set_axisbelow(True)
save(fig, "09_revenue_by_city")

# ══════════════════════════════════════════════════════════
# CHART 10: Payment Mode Distribution
# ══════════════════════════════════════════════════════════
pay_dist = orders["payment_mode"].value_counts()
fig, ax = plt.subplots(figsize=(8, 6))
colors_pay = [ZOMATO_RED, ACCENT, "#4CAF50", "#9C27B0", "#2196F3"]
wedges, texts, autos = ax.pie(
    pay_dist.values, labels=pay_dist.index, autopct="%1.1f%%",
    colors=colors_pay[:len(pay_dist)],
    wedgeprops=dict(linewidth=1.5, edgecolor=ZOMATO_DARK), startangle=90
)
for a in autos: a.set_color("white"); a.set_fontsize(9)
ax.set_title("💳 Payment Mode Distribution", fontsize=14)
save(fig, "10_payment_mode")

print(f"\n{'='*50}")
print(f"  ✅ EDA Complete! 10 charts saved to:")
print(f"  {OUT_DIR}")
print(f"{'='*50}")
