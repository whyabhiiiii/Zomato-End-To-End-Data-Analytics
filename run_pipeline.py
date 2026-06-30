#!/usr/bin/env python3
"""
============================================================
  Zomato End-to-End Data Analytics
  MASTER RUNNER — runs EDA + all 3 ML models in sequence
  Usage: python3 run_pipeline.py
============================================================
"""
import subprocess
import sys
import os

BASE = "/Users/abhishekkumar/Desktop/Zomato-End-To-End-Data-Analytics"

steps = [
    ("EDA & Charts",               f"{BASE}/Notebooks/eda.py"),
    ("Churn Prediction Model",     f"{BASE}/Models/train_churn_model.py"),
    ("Delivery Delay Model",       f"{BASE}/Models/train_delay_model.py"),
    ("Restaurant Rating Model",    f"{BASE}/Models/train_rating_model.py"),
]

print("=" * 60)
print("  🍕 ZOMATO ANALYTICS — MASTER PIPELINE RUNNER")
print("=" * 60)

for name, script in steps:
    print(f"\n▶  Running: {name}")
    print(f"   Script : {os.path.basename(script)}")
    print("-" * 40)
    result = subprocess.run([sys.executable, script], capture_output=False)
    if result.returncode != 0:
        print(f"❌ ERROR in {name} — pipeline stopped.")
        sys.exit(1)
    print(f"✅ {name} — Done")

print("\n" + "=" * 60)
print("  🎉 PIPELINE COMPLETE!")
print("  ├─ 10 EDA charts saved")
print("  ├─ 3 ML models trained & saved (.pkl)")
print("  └─ 7 ML visualisations saved")
print("=" * 60)
