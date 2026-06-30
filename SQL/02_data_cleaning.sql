-- ============================================================
-- Zomato End-to-End Data Analytics
-- 02_data_cleaning.sql  |  PostgreSQL
-- ============================================================

-- ── 1. NULL / MISSING VALUE CHECKS ───────────────────────────

SELECT 'users with null city'       AS check_name, COUNT(*) AS cnt FROM users WHERE city IS NULL
UNION ALL
SELECT 'orders with null amount',   COUNT(*) FROM orders WHERE final_amount IS NULL
UNION ALL
SELECT 'restaurants null rating',   COUNT(*) FROM restaurants WHERE rating IS NULL
UNION ALL
SELECT 'delivery null partner',     COUNT(*) FROM delivery WHERE partner_id IS NULL
UNION ALL
SELECT 'reviews null sentiment',    COUNT(*) FROM reviews WHERE sentiment IS NULL;

-- ── 2. DUPLICATE CHECKS ──────────────────────────────────────

-- Duplicate user IDs
SELECT user_id, COUNT(*) AS cnt
FROM users
GROUP BY user_id HAVING COUNT(*) > 1;

-- Duplicate restaurant IDs
SELECT restaurant_id, COUNT(*) AS cnt
FROM restaurants
GROUP BY restaurant_id HAVING COUNT(*) > 1;

-- Duplicate order IDs
SELECT order_id, COUNT(*) AS cnt
FROM orders
GROUP BY order_id HAVING COUNT(*) > 1;

-- ── 3. DATA SANITY CHECKS ────────────────────────────────────

-- Users: age outside valid range (16–90)
SELECT COUNT(*) AS invalid_age FROM users WHERE age < 16 OR age > 90;

-- Orders: suspiciously low final_amount (< ₹20)
SELECT order_id, final_amount FROM orders WHERE final_amount < 20;

-- Delivery: negative or zero delivery times
SELECT COUNT(*) AS invalid_delivery_time
FROM delivery WHERE actual_time_min <= 0 OR estimated_time_min <= 0;

-- Orders: final_amount > original amount (discount logic error)
SELECT COUNT(*) AS discount_error
FROM orders WHERE final_amount > order_amount;

-- Reviews: rating outside 1–5 range
SELECT COUNT(*) AS invalid_review_rating FROM reviews WHERE rating < 1 OR rating > 5;

-- Restaurants: rating outside 1–5 range
SELECT COUNT(*) AS invalid_rest_rating FROM restaurants WHERE rating < 1.0 OR rating > 5.0;

-- ── 4. CLEAN VIEWS ───────────────────────────────────────────

-- View: Only successfully delivered orders
CREATE OR REPLACE VIEW v_delivered_orders AS
SELECT * FROM orders WHERE order_status = 'Delivered';

-- View: Non-cancelled orders
CREATE OR REPLACE VIEW v_active_orders AS
SELECT * FROM orders WHERE order_status != 'Cancelled';

-- View: Gold members only
CREATE OR REPLACE VIEW v_gold_users AS
SELECT * FROM users WHERE is_gold_member = 1;

-- ── 5. STANDARDISE GENDER ────────────────────────────────────
UPDATE users SET gender = 'Male'
WHERE LOWER(gender) LIKE '%male%' AND gender <> 'Female';

-- ── 6. SUMMARY STATISTICS ────────────────────────────────────

-- Order amount distribution
SELECT
    MIN(final_amount)    AS min_order,
    MAX(final_amount)    AS max_order,
    ROUND(AVG(final_amount), 2) AS avg_order,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY final_amount) AS median_order
FROM orders WHERE order_status = 'Delivered';

-- Delivery time distribution
SELECT
    MIN(actual_time_min)  AS min_time,
    MAX(actual_time_min)  AS max_time,
    ROUND(AVG(actual_time_min), 1) AS avg_time,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY actual_time_min) AS median_time
FROM delivery;

-- Cancellation rate
SELECT
    order_status,
    COUNT(*) AS orders,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct
FROM orders
GROUP BY order_status;
