"""
============================================================
  Zomato End-to-End Data Analytics — Synthetic Data Generator
  Generates 6 interconnected CSV files (~585K rows total)
  Realistic patterns: peak hours, RFM behavior, Gold members,
  delivery delays, seasonal trends, sentiment labels
============================================================
"""

import pandas as pd
import numpy as np
import random
import os
from datetime import datetime, timedelta
from faker import Faker

fake = Faker("en_IN")
np.random.seed(42)
random.seed(42)

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "Data")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────
CITIES = {
    "Delhi":     ["Connaught Place", "Lajpat Nagar", "Rohini", "Dwarka", "Saket", "Hauz Khas", "Karol Bagh", "Janakpuri"],
    "Mumbai":    ["Bandra", "Andheri", "Juhu", "Colaba", "Powai", "Dadar", "Worli", "Malad"],
    "Bangalore": ["Koramangala", "Indiranagar", "Whitefield", "HSR Layout", "Jayanagar", "BTM Layout", "Marathahalli", "Yelahanka"],
    "Hyderabad": ["Banjara Hills", "Jubilee Hills", "Gachibowli", "HITEC City", "Secunderabad", "Madhapur", "Kukatpally", "Dilsukhnagar"],
    "Chennai":   ["Anna Nagar", "T Nagar", "Adyar", "Velachery", "OMR", "Nungambakkam", "Mylapore", "Porur"],
    "Pune":      ["Koregaon Park", "Viman Nagar", "Hinjewadi", "Kothrud", "Baner", "Aundh", "Kharadi", "Hadapsar"],
    "Kolkata":   ["Park Street", "Salt Lake", "New Town", "Ballygunge", "Behala", "Dum Dum", "Howrah", "Tollygunge"],
    "Ahmedabad": ["SG Highway", "Navrangpura", "Vastrapur", "Satellite", "Maninagar", "Paldi", "Bodakdev", "Prahlad Nagar"],
}

CUISINES = [
    "North Indian", "South Indian", "Chinese", "Mughlai", "Biryani",
    "Italian", "Continental", "Fast Food", "Desserts", "Cafe",
    "Rolls & Wraps", "Burger", "Pizza", "Seafood", "Bengali",
    "Rajasthani", "Punjabi", "Street Food", "Healthy Food", "Beverages"
]

RESTAURANT_TYPES = [
    "Quick Bites", "Casual Dining", "Fine Dining", "Food Court",
    "Cafe", "Bakery", "Sweet Shop", "Cloud Kitchen", "Dhaba", "Bar"
]

PAYMENT_MODES = ["UPI", "Credit Card", "Debit Card", "Cash", "Zomato Pay", "Net Banking"]
ORDER_STATUSES = ["Delivered", "Delivered", "Delivered", "Delivered", "Delivered",
                  "Delivered", "Delivered", "Cancelled", "Cancelled", "Refunded"]

MENU_CATEGORIES = {
    "North Indian": ["Butter Chicken", "Dal Makhani", "Paneer Tikka", "Naan", "Roti", "Biryani", "Chole Bhature", "Rajma Chawal"],
    "South Indian": ["Dosa", "Idli", "Sambhar", "Vada", "Uttapam", "Rava Dosa", "Appam", "Upma"],
    "Chinese":      ["Fried Rice", "Noodles", "Manchurian", "Spring Rolls", "Momos", "Chilli Paneer", "Hot & Sour Soup"],
    "Mughlai":      ["Seekh Kebab", "Shami Kebab", "Korma", "Nihari", "Haleem", "Phirni", "Mutton Rogan Josh"],
    "Biryani":      ["Chicken Biryani", "Mutton Biryani", "Veg Biryani", "Hyderabadi Biryani", "Egg Biryani", "Prawn Biryani"],
    "Italian":      ["Margherita Pizza", "Pasta Arrabiata", "Risotto", "Tiramisu", "Bruschetta", "Lasagne"],
    "Continental":  ["Grilled Chicken", "Fish & Chips", "Club Sandwich", "Caesar Salad", "Steak", "Soup"],
    "Fast Food":    ["Burger", "French Fries", "Nuggets", "Wrap", "Hot Dog", "Onion Rings"],
    "Desserts":     ["Gulab Jamun", "Rasgulla", "Kheer", "Ice Cream", "Brownie", "Cheesecake", "Jalebi"],
    "Cafe":         ["Cold Coffee", "Cappuccino", "Sandwich", "Waffle", "Smoothie", "Muffin", "Croissant"],
}

POSITIVE_REVIEWS = [
    "Absolutely loved the food! Delivery was super fast.",
    "Amazing taste, will order again for sure.",
    "Best biryani I've ever had. Highly recommended!",
    "Fresh ingredients, great packaging, on time delivery.",
    "Portion size was generous and the taste was fantastic.",
    "Great value for money. 5 stars from me!",
    "Food was piping hot when it arrived. Excellent!",
    "My family loved it. Ordering again next week.",
    "Authentic flavors, just like a home-cooked meal.",
    "Quick delivery, food tasted amazing. No complaints!",
]

NEUTRAL_REVIEWS = [
    "Food was okay, nothing extraordinary.",
    "Decent meal but a bit pricey for the portion size.",
    "Average experience, could be better.",
    "The taste was good but delivery took longer than expected.",
    "Food quality was fine. Not the best, not the worst.",
    "Packaging was not great but food tasted alright.",
    "Okay experience. May try again sometime.",
    "Standard food, nothing special to write home about.",
]

NEGATIVE_REVIEWS = [
    "Very disappointed. Food was cold and stale.",
    "Delivery was over an hour late. Food quality was poor.",
    "Not worth the money. Will not order again.",
    "Wrong items delivered. Customer support was unhelpful.",
    "Terrible packaging, food was spilled in the bag.",
    "Food had bad smell. Extremely unsatisfied.",
    "Very small portion for such a high price. Never again.",
    "Order arrived 2 hours late and was completely cold.",
]

print("🍕 Starting Zomato Data Generation...")
print("=" * 60)


# ─────────────────────────────────────────────
# 1. USERS TABLE (50,000 rows)
# ─────────────────────────────────────────────
print("📋 Generating users.csv (50,000 rows)...")

city_list = list(CITIES.keys())
city_weights = [0.20, 0.20, 0.18, 0.12, 0.10, 0.08, 0.07, 0.05]

users = []
for i in range(1, 50001):
    city = random.choices(city_list, weights=city_weights)[0]
    age = int(np.random.choice(
        range(18, 65),
        p=np.array([
            0.08 if x < 22 else
            0.035 if x < 35 else
            0.02 if x < 50 else
            0.008
            for x in range(18, 65)
        ]) / sum([
            0.08 if x < 22 else
            0.035 if x < 35 else
            0.02 if x < 50 else
            0.008
            for x in range(18, 65)
        ])
    ))
    signup_date = fake.date_between(start_date="-3y", end_date="-30d")
    is_gold = random.choices([1, 0], weights=[0.22, 0.78])[0]
    users.append({
        "user_id":       i,
        "name":          fake.name(),
        "age":           age,
        "gender":        random.choices(["Male", "Female", "Other"], weights=[0.52, 0.45, 0.03])[0],
        "city":          city,
        "locality":      random.choice(CITIES[city]),
        "occupation":    random.choices(
                            ["Student", "Salaried", "Self-Employed", "Homemaker", "Freelancer"],
                            weights=[0.20, 0.45, 0.20, 0.08, 0.07]
                         )[0],
        "marital_status": random.choices(["Single", "Married", "Divorced"], weights=[0.48, 0.46, 0.06])[0],
        "signup_date":   signup_date,
        "is_gold_member": is_gold,
        "phone":         fake.phone_number(),
    })

users_df = pd.DataFrame(users)
users_df.to_csv(os.path.join(OUTPUT_DIR, "users.csv"), index=False)
print(f"   ✅ users.csv saved ({len(users_df):,} rows)")


# ─────────────────────────────────────────────
# 2. RESTAURANTS TABLE (5,000 rows)
# ─────────────────────────────────────────────
print("🏪 Generating restaurants.csv (5,000 rows)...")

restaurants = []
for i in range(1, 5001):
    city = random.choices(city_list, weights=city_weights)[0]
    cuisine = random.choice(CUISINES)
    base_rating = np.random.normal(3.8, 0.7)
    rating = round(min(5.0, max(1.5, base_rating)), 1)
    votes = int(np.random.lognormal(5, 1.5))
    price_range = random.choices([1, 2, 3, 4], weights=[0.20, 0.35, 0.30, 0.15])[0]
    avg_cost = {1: random.randint(100, 250), 2: random.randint(250, 500),
                3: random.randint(500, 1000), 4: random.randint(1000, 3000)}[price_range]

    opening_year = random.randint(2010, 2023)
    restaurants.append({
        "restaurant_id":      i,
        "name":               f"{fake.last_name()}'s {random.choice(['Kitchen', 'Bistro', 'Dhaba', 'Cafe', 'House', 'Corner', 'Junction', 'Palace', 'Express', 'Garden'])}",
        "city":               city,
        "locality":           random.choice(CITIES[city]),
        "restaurant_type":    random.choice(RESTAURANT_TYPES),
        "cuisine":            cuisine,
        "rating":             rating,
        "votes":              votes,
        "price_range":        price_range,
        "avg_cost_for_two":   avg_cost,
        "online_delivery":    random.choices([1, 0], weights=[0.75, 0.25])[0],
        "table_booking":      random.choices([1, 0], weights=[0.35, 0.65])[0],
        "opening_year":       opening_year,
        "is_active":          random.choices([1, 0], weights=[0.92, 0.08])[0],
    })

restaurants_df = pd.DataFrame(restaurants)
restaurants_df.to_csv(os.path.join(OUTPUT_DIR, "restaurants.csv"), index=False)
print(f"   ✅ restaurants.csv saved ({len(restaurants_df):,} rows)")


# ─────────────────────────────────────────────
# 3. MENU TABLE (50,000 rows)
# ─────────────────────────────────────────────
print("🍽️  Generating menu.csv (50,000 rows)...")

menu = []
menu_id = 1
for _, rest in restaurants_df.iterrows():
    cuisine = rest["cuisine"]
    items = MENU_CATEGORIES.get(cuisine, MENU_CATEGORIES["Fast Food"])
    price_multiplier = rest["price_range"]
    n_items = random.randint(5, 20)
    for _ in range(n_items):
        item = random.choice(items)
        base_price = random.randint(80, 300) * price_multiplier
        menu.append({
            "menu_id":       menu_id,
            "restaurant_id": rest["restaurant_id"],
            "item_name":     item + ("" if random.random() > 0.3 else f" ({random.choice(['Special', 'Classic', 'Premium', 'Chef'])} Edition)"),
            "category":      cuisine,
            "price":         round(base_price + random.uniform(-20, 50), 0),
            "is_veg":        random.choices([1, 0], weights=[0.48, 0.52])[0],
            "is_bestseller": random.choices([1, 0], weights=[0.15, 0.85])[0],
        })
        menu_id += 1
        if menu_id > 50001:
            break
    if menu_id > 50001:
        break

menu_df = pd.DataFrame(menu)
menu_df.to_csv(os.path.join(OUTPUT_DIR, "menu.csv"), index=False)
print(f"   ✅ menu.csv saved ({len(menu_df):,} rows)")


# ─────────────────────────────────────────────
# 4. ORDERS TABLE (200,000 rows)
# ─────────────────────────────────────────────
print("📦 Generating orders.csv (200,000 rows)...")

# Build RFM profile per user: active, at-risk, churned
user_ids = users_df["user_id"].tolist()
user_profiles = {}
for uid in user_ids:
    profile_type = random.choices(["active", "at_risk", "churned"], weights=[0.55, 0.28, 0.17])[0]
    is_gold = users_df.loc[users_df["user_id"] == uid, "is_gold_member"].values[0]
    user_profiles[uid] = {"type": profile_type, "is_gold": is_gold}

active_restaurants = restaurants_df[restaurants_df["is_active"] == 1]["restaurant_id"].tolist()

orders = []
order_id = 1
start_date = datetime(2022, 1, 1)
end_date = datetime(2024, 12, 31)
date_range = (end_date - start_date).days

# Simulate 200,000 orders
sample_users = random.choices(user_ids, k=200000)

for uid in sample_users:
    profile = user_profiles[uid]

    # Date logic based on profile
    if profile["type"] == "active":
        days_back = random.randint(0, 180)
    elif profile["type"] == "at_risk":
        days_back = random.randint(45, 300)
    else:  # churned
        days_back = random.randint(200, 730)

    order_date = end_date - timedelta(days=days_back)
    if order_date < start_date:
        order_date = start_date + timedelta(days=random.randint(0, 60))

    # Peak hour simulation
    hour_weights = [1, 0.5, 0.3, 0.3, 0.4, 0.8, 1.5, 2, 3, 2.5, 2, 4, 5, 5,
                    4, 3, 3, 3.5, 4.5, 5, 5, 4.5, 3, 2]
    hour = random.choices(range(24), weights=hour_weights)[0]
    minute = random.randint(0, 59)

    rest_id = random.choice(active_restaurants)
    rest_row = restaurants_df[restaurants_df["restaurant_id"] == rest_id].iloc[0]

    # Gold member orders more and spends more
    gold_mult = 1.3 if profile["is_gold"] else 1.0
    base_amount = rest_row["avg_cost_for_two"] * random.uniform(0.4, 0.9) * gold_mult
    amount = round(max(50, base_amount + random.uniform(-50, 100)), 0)

    discount = 0
    if profile["is_gold"]:
        discount = round(amount * random.uniform(0.10, 0.30), 0)
    elif random.random() < 0.35:
        discount = round(amount * random.uniform(0.05, 0.20), 0)

    final_amount = max(30, amount - discount)

    status = random.choices(
        ["Delivered", "Cancelled", "Refunded"],
        weights=[0.88, 0.09, 0.03]
    )[0]

    orders.append({
        "order_id":        order_id,
        "user_id":         uid,
        "restaurant_id":   rest_id,
        "order_date":      order_date.strftime("%Y-%m-%d"),
        "order_time":      f"{hour:02d}:{minute:02d}:00",
        "order_amount":    int(amount),
        "discount_amount": int(discount),
        "final_amount":    int(final_amount),
        "payment_mode":    random.choices(
                              PAYMENT_MODES,
                              weights=[0.40, 0.20, 0.15, 0.12, 0.08, 0.05]
                           )[0],
        "order_status":    status,
        "items_count":     random.randint(1, 6),
    })
    order_id += 1

orders_df = pd.DataFrame(orders)
orders_df = orders_df.sort_values("order_date").reset_index(drop=True)
orders_df.to_csv(os.path.join(OUTPUT_DIR, "orders.csv"), index=False)
print(f"   ✅ orders.csv saved ({len(orders_df):,} rows)")


# ─────────────────────────────────────────────
# 5. REVIEWS TABLE (80,000 rows)
# ─────────────────────────────────────────────
print("⭐ Generating reviews.csv (80,000 rows)...")

delivered_orders = orders_df[orders_df["order_status"] == "Delivered"].sample(80000, random_state=42).reset_index(drop=True)

reviews = []
for idx, order in delivered_orders.iterrows():
    review_rating = random.choices([1, 2, 3, 4, 5], weights=[0.04, 0.06, 0.15, 0.35, 0.40])[0]

    if review_rating >= 4:
        review_text = random.choice(POSITIVE_REVIEWS)
        sentiment = "Positive"
    elif review_rating == 3:
        review_text = random.choice(NEUTRAL_REVIEWS)
        sentiment = "Neutral"
    else:
        review_text = random.choice(NEGATIVE_REVIEWS)
        sentiment = "Negative"

    reviews.append({
        "review_id":     idx + 1,
        "order_id":      order["order_id"],
        "user_id":       order["user_id"],
        "restaurant_id": order["restaurant_id"],
        "rating":        review_rating,
        "review_text":   review_text,
        "sentiment":     sentiment,
        "review_date":   order["order_date"],
    })

reviews_df = pd.DataFrame(reviews)
reviews_df.to_csv(os.path.join(OUTPUT_DIR, "reviews.csv"), index=False)
print(f"   ✅ reviews.csv saved ({len(reviews_df):,} rows)")


# ─────────────────────────────────────────────
# 6. DELIVERY TABLE (200,000 rows)
# ─────────────────────────────────────────────
print("🛵 Generating delivery.csv (200,000 rows)...")

n_partners = 2000
partner_ids = list(range(1, n_partners + 1))

delivery = []
for idx, order in orders_df.iterrows():
    if order["order_status"] == "Cancelled":
        continue

    distance = round(random.uniform(0.5, 15.0), 2)
    order_hour = int(order["order_time"][:2])

    # Peak hour delay factor
    is_peak = 1 if order_hour in [12, 13, 14, 19, 20, 21] else 0
    is_weekend = 1 if datetime.strptime(order["order_date"], "%Y-%m-%d").weekday() >= 5 else 0

    # Base estimated time: 1.5 min/km + 15 min prep
    estimated_mins = round(15 + distance * 1.8 + (is_peak * 10), 0)

    # Actual time with variation
    delay_prob = 0.10 + (distance / 15 * 0.15) + (is_peak * 0.15) + (is_weekend * 0.05)
    is_delayed = 1 if random.random() < delay_prob else 0

    if is_delayed:
        extra = random.randint(10, 45)
    else:
        extra = random.randint(-5, 8)

    actual_mins = max(10, estimated_mins + extra)
    delay_flag = 1 if actual_mins > estimated_mins + 10 else 0

    delivery.append({
        "delivery_id":       idx + 1,
        "order_id":          order["order_id"],
        "partner_id":        random.choice(partner_ids),
        "distance_km":       distance,
        "estimated_time_min": int(estimated_mins),
        "actual_time_min":   int(actual_mins),
        "delay_flag":        delay_flag,
        "is_peak_hour":      is_peak,
        "is_weekend":        is_weekend,
        "order_date":        order["order_date"],
        "order_hour":        order_hour,
    })

delivery_df = pd.DataFrame(delivery)
delivery_df.to_csv(os.path.join(OUTPUT_DIR, "delivery.csv"), index=False)
print(f"   ✅ delivery.csv saved ({len(delivery_df):,} rows)")


# ─────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("🎉 ALL DATA GENERATED SUCCESSFULLY!")
print("=" * 60)
total_rows = sum([
    len(users_df), len(restaurants_df), len(menu_df),
    len(orders_df), len(reviews_df), len(delivery_df)
])
print(f"   users.csv        → {len(users_df):>8,} rows")
print(f"   restaurants.csv  → {len(restaurants_df):>8,} rows")
print(f"   menu.csv         → {len(menu_df):>8,} rows")
print(f"   orders.csv       → {len(orders_df):>8,} rows")
print(f"   reviews.csv      → {len(reviews_df):>8,} rows")
print(f"   delivery.csv     → {len(delivery_df):>8,} rows")
print(f"   {'─'*30}")
print(f"   TOTAL            → {total_rows:>8,} rows")
print(f"\n📁 Data saved to: {os.path.abspath(OUTPUT_DIR)}")
print("=" * 60)
