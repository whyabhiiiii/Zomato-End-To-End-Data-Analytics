# 🍕 Zomato End-to-End Data Analytics

> **Live Dashboard:** [https://zomatics.streamlit.app](https://zomatics.streamlit.app) 🚀

> **A production-grade portfolio project** — from raw data generation to a live ML prediction web app.  
> Built to demonstrate end-to-end data engineering, SQL analytics, machine learning, and deployment skills.

---

## 🎯 Project Overview

This project replicates the full lifecycle of a data analytics role at a food-tech company like Zomato:

```
📊 Data Generation  →  🐘 SQL Analytics  →  🔍 EDA  →  🤖 ML Models  →  🌐 Flask Web App  →  🐳 Docker
```

**The differentiator**: Every layer connects to a real business question — not just academic exercises.

---

## 📊 Dataset at a Glance

| Table | Rows | Size | Purpose |
|---|---|---|---|
| `users.csv` | 200,000 | ~16 MB | Demographics, Gold status, city |
| `restaurants.csv` | 20,000 | ~1.6 MB | Metadata across 8 Indian cities |
| `menu.csv` | 200,001 | ~8.4 MB | Menu items, categories, pricing |
| `orders.csv` | 800,000 | ~52 MB | Core transaction fact table |
| `reviews.csv` | 320,000 | ~28.8 MB | Ratings, sentiment labels |
| `delivery.csv` | 728,281 | ~33.6 MB | Partner performance & delay flags |
| **Total** | **2,268,282** | **~140 MB** | |

### 🏙️ 8 Indian Cities
Bengaluru · Mumbai · Delhi NCR · Hyderabad · Chennai · Pune · Kolkata · Ahmedabad

### 📈 Realistic Data Patterns
- Peak-hour spikes at **lunch (12–2 PM)** and **dinner (7–10 PM)**
- **Gold members** spend 30% more and receive higher discounts
- RFM-encoded users: Active (55%) · At-Risk (28%) · Churned (17%)
- Delivery delays correlated with distance, peak hours, and weekends
- Sentiment labels (Positive/Neutral/Negative) on all reviews

---

## 🗄️ SQL Analytics (40 Queries Across 6 Sections)

| Section | Queries | Highlights |
|---|---|---|
| **A. Core KPIs** | Q1–Q6 | Revenue, AOV, Active Users, Discounts |
| **B. Restaurant Analytics** | Q7–Q16 | Pareto, RANK(), city-wise revenue |
| **C. Customer Analytics** | Q17–Q25 | RFM, CLV, Gold vs Regular, Churn |
| **D. Time-Based** | Q26–Q32 | MoM Growth, MAU, Running Totals |
| **E. Delivery Analytics** | Q33–Q37 | Delay rate, partner efficiency |
| **F. Advanced** | Q38–Q40 | Health Score, Sentiment, Executive KPI |

**SQL Concepts used**: Window functions (`RANK`, `NTILE`, `LAG`, `SUM OVER`), CTEs, CASE WHEN, subqueries, `PERCENTILE_CONT`, `DATE_TRUNC`

---

## 🤖 Machine Learning — 3 Models

### Model 1: Customer Churn Prediction
- **Algorithm**: Random Forest Classifier
- **Features**: 15 (Recency, Frequency, Monetary, Review sentiment, Delivery experience, Demographics)
- **Training set**: 48,497 users
- **Key insight**: RFM recency is the #1 churn predictor

### Model 2: Delivery Delay Prediction
- **Algorithm**: Gradient Boosting Classifier
- **Features**: 10 (Distance, Peak hour, City, Restaurant type, Order size)
- **Dataset**: 182,386 deliveries
- **Delay rate**: 24.9% baseline

### Model 3: Restaurant Rating Prediction
- **Algorithm**: Random Forest Regressor
- **Features**: 19 (Revenue, Review sentiment, Delivery speed, Location, Cuisine)
- **Dataset**: 5,000 restaurants

---

## 🌐 Web Applications

### 1. Live Streamlit Analytics Dashboard
**URL:** [https://zomatics.streamlit.app](https://zomatics.streamlit.app)
- Interactive KPI tracking (Revenue, Active Users, Delay Rates)
- Dynamic city and cuisine level filtering
- RFM segmentation visualizations (Treemaps)
- Geospatial sentiment analysis

### 2. Flask ML Predictors
3-predictor web app with Zomato-branded dark UI:

| Page | URL | Description |
|---|---|---|
| **Dashboard** | `/` | Live KPIs, ML tools overview, dataset info |
| **Churn Predictor** | `/churn` | 15-input form with risk tiers & probability bar |
| **Delay Predictor** | `/delay` | 10-input form predicting late deliveries |
| **Rating Predictor** | `/rating` | 19-input form for restaurant rating forecast |

---

## 🚀 Quick Start

### 1. Generate the Data
```bash
python3 generate_data/generate_zomato_data.py
```

### 2. Run the Full ML Pipeline
```bash
python3 run_pipeline.py
```
This runs EDA (10 charts) + trains all 3 models in sequence.

### 3. Launch the Web App
```bash
cd app
python3 app.py
# Open: http://localhost:5000
```

### 4. Load SQL in PostgreSQL
```sql
\i SQL/01_schema.sql
-- Load CSVs using COPY command
\i SQL/02_data_cleaning.sql
\i SQL/03_analysis_queries.sql
```

---

## 🐳 Docker Deployment

```bash
# Build
docker build -t zomato-analytics .

# Run
docker run -p 5000:5000 zomato-analytics
```

---

## 📁 Project Structure

```
Zomato-End-To-End-Data-Analytics/
├── 📂 Data/                    # 6 CSV files (~2.26M rows)
├── 📂 generate_data/           # Synthetic data generator
│   └── generate_zomato_data.py
├── 📂 SQL/
│   ├── 01_schema.sql           # PostgreSQL schema + indexes
│   ├── 02_data_cleaning.sql    # QA checks + clean views
│   └── 03_analysis_queries.sql # 40 business queries
├── 📂 Notebooks/
│   └── eda.py                  # 10 Zomato-branded charts
├── 📂 Models/
│   ├── train_churn_model.py    # RF Churn classifier
│   ├── train_delay_model.py    # GB Delay classifier
│   ├── train_rating_model.py   # RF Rating regressor
│   ├── churn_model.pkl
│   ├── delay_model.pkl
│   └── rating_model.pkl
├── 📂 app/
│   ├── app.py                  # Flask backend
│   └── templates/              # 4 HTML pages
├── 📂 Dashboard/
│   └── Dashboard_Screenshots/  # 17 charts (EDA + ML)
├── 📂 Documentation/
├── run_pipeline.py             # Master runner
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## 💡 Business Insights Discovered

1. **Gold Members** have 30% higher AOV and 2x lower churn rate — Gold program drives disproportionate revenue
2. **Dinner peak (7–10 PM)** generates 3x more orders than any other window — optimal for surge pricing
3. **Top 20% of restaurants** generate 80% of platform revenue (Pareto holds)
4. **Deliveries > 5 km** have 40%+ delay rate — distance is the biggest delay predictor
5. **Review sentiment** is a leading indicator of restaurant rating — 3-week lag effect

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Data Generation | Python 3.13 + Faker |
| SQL Analytics | PostgreSQL 16 |
| EDA | Pandas, Matplotlib, Seaborn |
| Machine Learning | scikit-learn (Random Forest, Gradient Boosting) |
| Web Framework | Flask 3.1, Streamlit 1.42 |
| Deployment | Docker, Streamlit Community Cloud |
| Dashboard | Streamlit, Tableau Public |

---

## 👤 Author

Built as a job-ready portfolio project demonstrating end-to-end data analytics skills:
- Data Engineering (synthetic dataset design)
- SQL Analytics (window functions, CTEs, business KPIs)
- Machine Learning (classification + regression pipelines)
- Data Visualization (Matplotlib/Seaborn)
- Web Development (Flask REST API)
- DevOps (Dockerization)

---

*⭐ If this project helped you, give it a star!*
