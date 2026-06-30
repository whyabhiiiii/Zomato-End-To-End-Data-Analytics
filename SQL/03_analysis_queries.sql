-- ============================================================
-- Zomato End-to-End Data Analytics
-- 03_analysis_queries.sql  |  40 Business Queries
-- PostgreSQL  |  Sections: KPIs, Restaurants, Customers,
--             Time-Based, Delivery, Advanced Analytics
-- ============================================================

-- ═══════════════════════════════════════════════════════════
-- SECTION A: CORE KPIs  (Q1–Q6)
-- ═══════════════════════════════════════════════════════════

-- Q1. Total Revenue (delivered orders only)
SELECT TO_CHAR(SUM(final_amount), 'FM₹999,999,999') AS total_revenue
FROM orders WHERE order_status = 'Delivered';

-- Q2. Total Orders placed on the platform
SELECT COUNT(order_id) AS total_orders FROM orders;

-- Q3. Average Order Value (AOV)
SELECT ROUND(AVG(final_amount), 2) AS aov
FROM orders WHERE order_status = 'Delivered';

-- Q4. Total Active Users (placed at least 1 order)
SELECT COUNT(DISTINCT user_id) AS active_users FROM orders;

-- Q5. Total Active Restaurants
SELECT COUNT(*) AS active_restaurants FROM restaurants WHERE is_active = 1;

-- Q6. Total Discounts Given to Customers
SELECT TO_CHAR(SUM(discount_amount), 'FM₹999,999,999') AS total_discounts
FROM orders;

-- ═══════════════════════════════════════════════════════════
-- SECTION B: RESTAURANT ANALYTICS  (Q7–Q16)
-- ═══════════════════════════════════════════════════════════

-- Q7. Top 10 Restaurants by Revenue
SELECT r.name, r.city, r.cuisine,
       SUM(o.final_amount) AS revenue,
       COUNT(o.order_id) AS total_orders
FROM orders o
JOIN restaurants r ON o.restaurant_id = r.restaurant_id
WHERE o.order_status = 'Delivered'
GROUP BY r.name, r.city, r.cuisine
ORDER BY revenue DESC LIMIT 10;

-- Q8. Top 10 Restaurants by Order Count
SELECT r.name, r.city, COUNT(o.order_id) AS total_orders,
       SUM(o.final_amount) AS revenue
FROM orders o
JOIN restaurants r ON o.restaurant_id = r.restaurant_id
GROUP BY r.name, r.city
ORDER BY total_orders DESC LIMIT 10;

-- Q9. Revenue by Cuisine Type
SELECT r.cuisine,
       SUM(o.final_amount) AS revenue,
       COUNT(o.order_id) AS orders,
       ROUND(AVG(o.final_amount), 2) AS avg_order_value
FROM orders o
JOIN restaurants r ON o.restaurant_id = r.restaurant_id
WHERE o.order_status = 'Delivered'
GROUP BY r.cuisine
ORDER BY revenue DESC;

-- Q10. Revenue % Contribution by Restaurant (Pareto)
SELECT r.name,
       SUM(o.final_amount) AS revenue,
       ROUND(100.0 * SUM(o.final_amount) / SUM(SUM(o.final_amount)) OVER (), 2) AS revenue_pct,
       SUM(SUM(o.final_amount)) OVER (ORDER BY SUM(o.final_amount) DESC) AS cumulative_revenue
FROM orders o
JOIN restaurants r ON o.restaurant_id = r.restaurant_id
WHERE o.order_status = 'Delivered'
GROUP BY r.name
ORDER BY revenue DESC;

-- Q11. Top Revenue Restaurant per City (RANK window function)
SELECT * FROM (
    SELECT r.city, r.name, SUM(o.final_amount) AS revenue,
           RANK() OVER (PARTITION BY r.city ORDER BY SUM(o.final_amount) DESC) AS city_rank
    FROM orders o
    JOIN restaurants r ON o.restaurant_id = r.restaurant_id
    WHERE o.order_status = 'Delivered'
    GROUP BY r.city, r.name
) ranked
WHERE city_rank = 1
ORDER BY revenue DESC;

-- Q12. Online Delivery vs Dine-In Revenue Split
SELECT
    CASE r.online_delivery WHEN 1 THEN 'Online Delivery' ELSE 'Dine-In Only' END AS delivery_type,
    COUNT(DISTINCT r.restaurant_id) AS restaurants,
    SUM(o.final_amount) AS revenue,
    COUNT(o.order_id) AS orders,
    ROUND(AVG(o.final_amount), 2) AS avg_order_value
FROM orders o
JOIN restaurants r ON o.restaurant_id = r.restaurant_id
WHERE o.order_status = 'Delivered'
GROUP BY r.online_delivery;

-- Q13. Average Rating & Votes by City
SELECT city,
       ROUND(AVG(rating), 2) AS avg_rating,
       SUM(votes) AS total_votes,
       COUNT(*) AS restaurant_count
FROM restaurants
WHERE rating IS NOT NULL
GROUP BY city
ORDER BY avg_rating DESC;

-- Q14. Revenue by Price Range Tier
SELECT r.price_range,
       CASE r.price_range
           WHEN 1 THEN 'Budget (₹<200)'
           WHEN 2 THEN 'Mid-Range (₹200–400)'
           WHEN 3 THEN 'Premium (₹400–700)'
           WHEN 4 THEN 'Luxury (₹700+)'
       END AS tier_name,
       COUNT(DISTINCT r.restaurant_id) AS restaurants,
       SUM(o.final_amount) AS revenue,
       COUNT(o.order_id) AS orders
FROM orders o
JOIN restaurants r ON o.restaurant_id = r.restaurant_id
WHERE o.order_status = 'Delivered'
GROUP BY r.price_range
ORDER BY r.price_range;

-- Q15. Revenue vs Rating Correlation (for scatter plot)
SELECT r.name, r.rating, r.votes,
       SUM(o.final_amount) AS revenue,
       COUNT(o.order_id) AS orders
FROM orders o
JOIN restaurants r ON o.restaurant_id = r.restaurant_id
WHERE r.rating IS NOT NULL AND o.order_status = 'Delivered'
GROUP BY r.name, r.rating, r.votes
ORDER BY r.rating DESC;

-- Q16. Pareto: Top 20% Restaurants Driving 80% Revenue
WITH rest_rev AS (
    SELECT r.restaurant_id, r.name,
           SUM(o.final_amount) AS revenue,
           NTILE(5) OVER (ORDER BY SUM(o.final_amount) ASC) AS quintile
    FROM orders o
    JOIN restaurants r ON o.restaurant_id = r.restaurant_id
    WHERE o.order_status = 'Delivered'
    GROUP BY r.restaurant_id, r.name
),
totals AS (
    SELECT SUM(revenue) AS total_rev FROM rest_rev
)
SELECT name, revenue, quintile,
       ROUND(100.0 * revenue / totals.total_rev, 4) AS pct_of_total
FROM rest_rev, totals
WHERE quintile = 5
ORDER BY revenue DESC;

-- ═══════════════════════════════════════════════════════════
-- SECTION C: CUSTOMER ANALYTICS  (Q17–Q25)
-- ═══════════════════════════════════════════════════════════

-- Q17. Revenue by Gender
SELECT u.gender,
       COUNT(DISTINCT o.user_id) AS users,
       SUM(o.final_amount) AS revenue,
       COUNT(o.order_id) AS orders,
       ROUND(AVG(o.final_amount), 2) AS avg_order_value
FROM orders o
JOIN users u ON o.user_id = u.user_id
WHERE o.order_status = 'Delivered'
GROUP BY u.gender
ORDER BY revenue DESC;

-- Q18. Revenue by Age Group (Generation Segmentation)
SELECT
    CASE
        WHEN u.age < 22 THEN 'Gen Z (<22)'
        WHEN u.age BETWEEN 22 AND 35 THEN 'Millennials (22–35)'
        WHEN u.age BETWEEN 36 AND 50 THEN 'Gen X (36–50)'
        ELSE 'Boomers (50+)'
    END AS age_group,
    COUNT(DISTINCT o.user_id) AS users,
    SUM(o.final_amount) AS revenue,
    COUNT(o.order_id) AS orders,
    ROUND(AVG(o.final_amount), 2) AS avg_order_value
FROM orders o
JOIN users u ON o.user_id = u.user_id
WHERE o.order_status = 'Delivered'
GROUP BY age_group
ORDER BY revenue DESC;

-- Q19. Revenue by Occupation
SELECT u.occupation,
       COUNT(DISTINCT o.user_id) AS users,
       SUM(o.final_amount) AS revenue,
       ROUND(AVG(o.final_amount), 2) AS avg_order_value
FROM orders o
JOIN users u ON o.user_id = u.user_id
WHERE o.order_status = 'Delivered'
GROUP BY u.occupation
ORDER BY revenue DESC;

-- Q20. Gold Members vs Regular Members (key insight)
SELECT
    CASE u.is_gold_member WHEN 1 THEN 'Gold Member' ELSE 'Regular' END AS member_type,
    COUNT(DISTINCT o.user_id) AS users,
    SUM(o.final_amount) AS total_revenue,
    ROUND(AVG(o.final_amount), 2) AS avg_order_value,
    ROUND(AVG(o.discount_amount), 2) AS avg_discount,
    COUNT(o.order_id) AS total_orders,
    ROUND(AVG(COUNT(o.order_id)) OVER (PARTITION BY u.is_gold_member), 1) AS avg_orders_per_user
FROM orders o
JOIN users u ON o.user_id = u.user_id
WHERE o.order_status = 'Delivered'
GROUP BY u.is_gold_member;

-- Q21. Customer Lifetime Value (CLV) — Top 50
SELECT u.user_id, u.name, u.city, u.is_gold_member,
       COUNT(o.order_id) AS total_orders,
       SUM(o.final_amount) AS lifetime_value,
       ROUND(AVG(o.final_amount), 2) AS avg_order_value,
       MIN(o.order_date) AS first_order,
       MAX(o.order_date) AS last_order,
       MAX(o.order_date) - MIN(o.order_date) AS customer_tenure_days
FROM users u
JOIN orders o ON u.user_id = o.user_id
WHERE o.order_status = 'Delivered'
GROUP BY u.user_id, u.name, u.city, u.is_gold_member
ORDER BY lifetime_value DESC LIMIT 50;

-- Q22. RFM Segmentation (Industry-Standard)
WITH rfm AS (
    SELECT user_id,
           MAX(order_date) AS last_order_date,
           COUNT(order_id) AS frequency,
           SUM(final_amount) AS monetary,
           CURRENT_DATE - MAX(order_date) AS recency_days
    FROM orders
    WHERE order_status = 'Delivered'
    GROUP BY user_id
),
rfm_scored AS (
    SELECT *,
           NTILE(5) OVER (ORDER BY recency_days DESC) AS r_score,
           NTILE(5) OVER (ORDER BY frequency ASC)     AS f_score,
           NTILE(5) OVER (ORDER BY monetary ASC)      AS m_score
    FROM rfm
)
SELECT user_id, last_order_date, frequency, monetary, recency_days,
       r_score, f_score, m_score,
       CASE
           WHEN r_score >= 4 AND f_score >= 4 THEN 'Champions'
           WHEN r_score >= 3 AND f_score >= 3 THEN 'Loyal Customers'
           WHEN r_score >= 4 AND f_score < 2  THEN 'New Customers'
           WHEN r_score BETWEEN 2 AND 3 AND f_score >= 3 THEN 'Potential Loyalists'
           WHEN r_score < 2 AND f_score >= 3  THEN 'At Risk'
           WHEN r_score < 2 AND f_score < 2   THEN 'Lost'
           ELSE 'Needs Attention'
       END AS rfm_segment
FROM rfm_scored
ORDER BY monetary DESC;

-- Q23. Churn Indicators — Users Inactive 90+ Days
SELECT u.user_id, u.name, u.city, u.is_gold_member,
       MAX(o.order_date) AS last_order_date,
       CURRENT_DATE - MAX(o.order_date) AS days_inactive,
       COUNT(o.order_id) AS lifetime_orders,
       SUM(o.final_amount) AS lifetime_value
FROM users u
JOIN orders o ON u.user_id = o.user_id
GROUP BY u.user_id, u.name, u.city, u.is_gold_member
HAVING MAX(o.order_date) < CURRENT_DATE - INTERVAL '90 days'
ORDER BY days_inactive DESC;

-- Q24. Repeat vs One-Time Users
SELECT customer_type,
       COUNT(*) AS total_users,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct
FROM (
    SELECT user_id,
           CASE WHEN COUNT(order_id) = 1 THEN 'One-Time' ELSE 'Repeat' END AS customer_type
    FROM orders
    GROUP BY user_id
) t
GROUP BY customer_type;

-- Q25. First vs Repeat Order Revenue
WITH ranked_orders AS (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY order_date) AS order_rank
    FROM orders WHERE order_status = 'Delivered'
)
SELECT
    CASE WHEN order_rank = 1 THEN 'First Order' ELSE 'Repeat Order' END AS order_type,
    COUNT(*) AS orders,
    SUM(final_amount) AS revenue,
    ROUND(AVG(final_amount), 2) AS avg_order_value
FROM ranked_orders
GROUP BY order_type;

-- ═══════════════════════════════════════════════════════════
-- SECTION D: TIME-BASED ANALYTICS  (Q26–Q32)
-- ═══════════════════════════════════════════════════════════

-- Q26. Monthly Revenue Trend
SELECT DATE_TRUNC('month', order_date) AS month,
       SUM(final_amount) AS monthly_revenue,
       COUNT(order_id) AS monthly_orders,
       ROUND(AVG(final_amount), 2) AS avg_order_value
FROM orders
WHERE order_status = 'Delivered'
GROUP BY month
ORDER BY month;

-- Q27. Month-over-Month Revenue Growth %
WITH monthly AS (
    SELECT DATE_TRUNC('month', order_date) AS month,
           SUM(final_amount) AS revenue
    FROM orders WHERE order_status = 'Delivered'
    GROUP BY month
)
SELECT month, revenue,
       LAG(revenue) OVER (ORDER BY month) AS prev_month_revenue,
       ROUND(100.0 * (revenue - LAG(revenue) OVER (ORDER BY month))
             / NULLIF(LAG(revenue) OVER (ORDER BY month), 0), 2) AS mom_growth_pct
FROM monthly
ORDER BY month;

-- Q28. Cumulative Revenue (Running Total)
SELECT order_date,
       SUM(final_amount) AS daily_revenue,
       SUM(SUM(final_amount)) OVER (ORDER BY order_date) AS cumulative_revenue
FROM orders
WHERE order_status = 'Delivered'
GROUP BY order_date
ORDER BY order_date;

-- Q29. Monthly Active Users (MAU)
SELECT DATE_TRUNC('month', order_date) AS month,
       COUNT(DISTINCT user_id) AS monthly_active_users
FROM orders
GROUP BY month
ORDER BY month;

-- Q30. New User Acquisition per Month
SELECT TO_CHAR(first_order_date, 'MM/YYYY') AS month_year,
       COUNT(user_id) AS new_users
FROM (
    SELECT user_id, MIN(order_date) AS first_order_date
    FROM orders GROUP BY user_id
) t
GROUP BY month_year, DATE_TRUNC('month', first_order_date)
ORDER BY DATE_TRUNC('month', first_order_date);

-- Q31. Revenue & Delivery Time by Hour of Day (Peak Hour Analysis)
SELECT EXTRACT(HOUR FROM o.order_time)::INT AS order_hour,
       COUNT(o.order_id) AS orders,
       SUM(o.final_amount) AS revenue,
       ROUND(AVG(d.actual_time_min), 1) AS avg_delivery_min
FROM orders o
LEFT JOIN delivery d ON o.order_id = d.order_id
WHERE o.order_status = 'Delivered'
GROUP BY order_hour
ORDER BY order_hour;

-- Q32. Weekend vs Weekday Performance
SELECT
    CASE d.is_weekend WHEN 1 THEN 'Weekend' ELSE 'Weekday' END AS day_type,
    COUNT(o.order_id) AS orders,
    SUM(o.final_amount) AS revenue,
    ROUND(AVG(d.actual_time_min), 1) AS avg_delivery_min,
    ROUND(100.0 * AVG(d.delay_flag::NUMERIC), 2) AS delay_rate_pct
FROM delivery d
JOIN orders o ON d.order_id = o.order_id
WHERE o.order_status = 'Delivered'
GROUP BY d.is_weekend;

-- ═══════════════════════════════════════════════════════════
-- SECTION E: DELIVERY ANALYTICS  (Q33–Q37)
-- ═══════════════════════════════════════════════════════════

-- Q33. Average Delivery Time by City
SELECT r.city,
       COUNT(d.delivery_id) AS total_deliveries,
       ROUND(AVG(d.estimated_time_min), 1) AS avg_estimated_min,
       ROUND(AVG(d.actual_time_min), 1) AS avg_actual_min,
       ROUND(AVG(d.actual_time_min - d.estimated_time_min), 1) AS avg_delay_min
FROM delivery d
JOIN orders o ON d.order_id = o.order_id
JOIN restaurants r ON o.restaurant_id = r.restaurant_id
GROUP BY r.city
ORDER BY avg_actual_min DESC;

-- Q34. Delay Rate by City
SELECT r.city,
       COUNT(*) AS total_deliveries,
       SUM(d.delay_flag) AS delayed_count,
       ROUND(100.0 * SUM(d.delay_flag) / COUNT(*), 2) AS delay_rate_pct
FROM delivery d
JOIN orders o ON d.order_id = o.order_id
JOIN restaurants r ON o.restaurant_id = r.restaurant_id
GROUP BY r.city
ORDER BY delay_rate_pct DESC;

-- Q35. Delay Rate by Distance Tier
SELECT
    CASE
        WHEN d.distance_km < 2 THEN '< 2 km'
        WHEN d.distance_km BETWEEN 2 AND 5 THEN '2–5 km'
        WHEN d.distance_km BETWEEN 5 AND 10 THEN '5–10 km'
        ELSE '> 10 km'
    END AS distance_tier,
    COUNT(*) AS deliveries,
    SUM(d.delay_flag) AS delayed,
    ROUND(100.0 * SUM(d.delay_flag) / COUNT(*), 2) AS delay_rate_pct,
    ROUND(AVG(d.actual_time_min), 1) AS avg_actual_min
FROM delivery d
GROUP BY distance_tier
ORDER BY delay_rate_pct DESC;

-- Q36. Top 20 Delivery Partners by Volume & Efficiency
SELECT partner_id,
       COUNT(*) AS total_deliveries,
       SUM(delay_flag) AS delays,
       ROUND(100.0 * SUM(delay_flag) / COUNT(*), 2) AS delay_rate_pct,
       ROUND(AVG(actual_time_min), 1) AS avg_delivery_min,
       ROUND(AVG(distance_km), 1) AS avg_distance_km
FROM delivery
GROUP BY partner_id
ORDER BY total_deliveries DESC LIMIT 20;

-- Q37. Peak Hour vs Off-Peak Delivery Comparison
SELECT
    CASE is_peak_hour WHEN 1 THEN 'Peak Hour' ELSE 'Off-Peak' END AS time_type,
    COUNT(*) AS deliveries,
    SUM(delay_flag) AS delayed_count,
    ROUND(100.0 * SUM(delay_flag) / COUNT(*), 2) AS delay_rate_pct,
    ROUND(AVG(actual_time_min), 1) AS avg_time_min,
    ROUND(AVG(distance_km), 2) AS avg_distance_km
FROM delivery
GROUP BY is_peak_hour;

-- ═══════════════════════════════════════════════════════════
-- SECTION F: ADVANCED ANALYTICS  (Q38–Q40)
-- ═══════════════════════════════════════════════════════════

-- Q38. Sentiment Summary per Restaurant
SELECT r.name, r.city, r.cuisine,
       COUNT(rv.review_id) AS total_reviews,
       SUM(CASE WHEN rv.sentiment = 'Positive' THEN 1 ELSE 0 END) AS positive,
       SUM(CASE WHEN rv.sentiment = 'Neutral'  THEN 1 ELSE 0 END) AS neutral,
       SUM(CASE WHEN rv.sentiment = 'Negative' THEN 1 ELSE 0 END) AS negative,
       ROUND(100.0 * SUM(CASE WHEN rv.sentiment = 'Positive' THEN 1 ELSE 0 END)
             / COUNT(rv.review_id), 1) AS positive_pct,
       ROUND(AVG(rv.rating), 2) AS avg_review_rating
FROM reviews rv
JOIN restaurants r ON rv.restaurant_id = r.restaurant_id
GROUP BY r.name, r.city, r.cuisine
ORDER BY positive_pct DESC LIMIT 30;

-- Q39. Restaurant Health Score (Composite Metric)
-- Weights: 40% Revenue + 30% Rating + 20% Sentiment + 10% Delivery Speed
WITH rev_rank AS (
    SELECT restaurant_id,
           NTILE(10) OVER (ORDER BY SUM(final_amount)) AS rev_score
    FROM orders WHERE order_status = 'Delivered'
    GROUP BY restaurant_id
),
sentiment_rank AS (
    SELECT restaurant_id,
           ROUND(100.0 * SUM(CASE WHEN sentiment = 'Positive' THEN 1 ELSE 0 END) / COUNT(*), 1) AS pos_pct
    FROM reviews GROUP BY restaurant_id
),
delivery_rank AS (
    SELECT o.restaurant_id,
           NTILE(10) OVER (ORDER BY AVG(d.actual_time_min) DESC) AS speed_score
    FROM delivery d
    JOIN orders o ON d.order_id = o.order_id
    GROUP BY o.restaurant_id
)
SELECT r.name, r.city, r.cuisine, r.rating,
       ROUND(
           0.4 * COALESCE(rv.rev_score, 5)
         + 0.3 * (COALESCE(r.rating, 3.0) * 2)
         + 0.2 * COALESCE(s.pos_pct / 10, 5)
         + 0.1 * COALESCE(dr.speed_score, 5)
       , 2) AS health_score
FROM restaurants r
LEFT JOIN rev_rank rv ON r.restaurant_id = rv.restaurant_id
LEFT JOIN sentiment_rank s ON r.restaurant_id = s.restaurant_id
LEFT JOIN delivery_rank dr ON r.restaurant_id = dr.restaurant_id
WHERE r.is_active = 1
ORDER BY health_score DESC LIMIT 30;

-- Q40. Executive Business Health Dashboard (Single-Row Summary)
SELECT
    (SELECT TO_CHAR(SUM(final_amount), 'FM₹999,999,999')
     FROM orders WHERE order_status = 'Delivered')                                     AS total_revenue,

    (SELECT COUNT(*) FROM orders)                                                       AS total_orders,

    (SELECT ROUND(AVG(final_amount), 2)
     FROM orders WHERE order_status = 'Delivered')                                     AS avg_order_value,

    (SELECT COUNT(DISTINCT user_id) FROM orders)                                        AS active_users,

    (SELECT COUNT(*) FROM restaurants WHERE is_active = 1)                             AS active_restaurants,

    (SELECT ROUND(100.0 * SUM(CASE WHEN order_status = 'Cancelled' THEN 1 ELSE 0 END)
                       / COUNT(*), 2) FROM orders)                                     AS cancellation_rate_pct,

    (SELECT ROUND(AVG(actual_time_min), 1) FROM delivery)                              AS avg_delivery_min,

    (SELECT ROUND(100.0 * SUM(delay_flag) / COUNT(*), 2) FROM delivery)               AS overall_delay_rate_pct,

    (SELECT city FROM (
        SELECT r.city, SUM(o.final_amount) AS rev
        FROM orders o JOIN restaurants r ON o.restaurant_id = r.restaurant_id
        WHERE o.order_status = 'Delivered'
        GROUP BY r.city ORDER BY rev DESC LIMIT 1
    ) t)                                                                               AS top_city,

    (SELECT cuisine FROM (
        SELECT r.cuisine, SUM(o.final_amount) AS rev
        FROM orders o JOIN restaurants r ON o.restaurant_id = r.restaurant_id
        WHERE o.order_status = 'Delivered'
        GROUP BY r.cuisine ORDER BY rev DESC LIMIT 1
    ) t)                                                                               AS top_cuisine,

    (SELECT ROUND(100.0 * COUNT(DISTINCT CASE WHEN is_gold_member = 1 THEN user_id END)
                       / COUNT(DISTINCT user_id), 2) FROM users)                       AS gold_member_pct;
