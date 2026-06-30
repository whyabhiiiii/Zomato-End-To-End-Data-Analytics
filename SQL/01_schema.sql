-- ============================================================
-- Zomato End-to-End Data Analytics
-- 01_schema.sql  |  PostgreSQL
-- ============================================================

-- 1. USERS
DROP TABLE IF EXISTS users CASCADE;
CREATE TABLE users (
    user_id        INT PRIMARY KEY,
    name           TEXT,
    age            INT,
    gender         TEXT,
    city           TEXT,
    locality       TEXT,
    occupation     TEXT,
    marital_status TEXT,
    signup_date    DATE,
    is_gold_member INT,  -- 0 or 1
    phone          TEXT
);

-- 2. RESTAURANTS
DROP TABLE IF EXISTS restaurants CASCADE;
CREATE TABLE restaurants (
    restaurant_id     INT PRIMARY KEY,
    name              TEXT,
    city              TEXT,
    locality          TEXT,
    restaurant_type   TEXT,
    cuisine           TEXT,
    rating            NUMERIC(3,1),
    votes             INT,
    price_range       INT,          -- 1 (cheap) to 4 (premium)
    avg_cost_for_two  INT,
    online_delivery   INT,
    table_booking     INT,
    opening_year      INT,
    is_active         INT
);

-- 3. MENU
DROP TABLE IF EXISTS menu CASCADE;
CREATE TABLE menu (
    menu_id       BIGINT PRIMARY KEY,
    restaurant_id INT REFERENCES restaurants(restaurant_id),
    item_name     TEXT,
    category      TEXT,
    price         NUMERIC(10,2),
    is_veg        INT,
    is_bestseller INT
);

-- 4. ORDERS
DROP TABLE IF EXISTS orders CASCADE;
CREATE TABLE orders (
    order_id        BIGINT PRIMARY KEY,
    user_id         INT REFERENCES users(user_id),
    restaurant_id   INT REFERENCES restaurants(restaurant_id),
    order_date      DATE,
    order_time      TIME,
    order_amount    INT,
    discount_amount INT,
    final_amount    INT,
    payment_mode    TEXT,
    order_status    TEXT,
    items_count     INT
);

-- 5. REVIEWS
DROP TABLE IF EXISTS reviews CASCADE;
CREATE TABLE reviews (
    review_id     BIGINT PRIMARY KEY,
    order_id      BIGINT REFERENCES orders(order_id),
    user_id       INT REFERENCES users(user_id),
    restaurant_id INT REFERENCES restaurants(restaurant_id),
    rating        INT,
    review_text   TEXT,
    sentiment     TEXT,
    review_date   DATE
);

-- 6. DELIVERY
DROP TABLE IF EXISTS delivery CASCADE;
CREATE TABLE delivery (
    delivery_id         BIGINT PRIMARY KEY,
    order_id            BIGINT REFERENCES orders(order_id),
    partner_id          INT,
    distance_km         NUMERIC(5,2),
    estimated_time_min  INT,
    actual_time_min     INT,
    delay_flag          INT,
    is_peak_hour        INT,
    is_weekend          INT,
    order_date          DATE,
    order_hour          INT
);

-- INDEXES for performance
CREATE INDEX idx_orders_user     ON orders(user_id);
CREATE INDEX idx_orders_rest     ON orders(restaurant_id);
CREATE INDEX idx_orders_date     ON orders(order_date);
CREATE INDEX idx_delivery_order  ON delivery(order_id);
CREATE INDEX idx_reviews_rest    ON reviews(restaurant_id);

-- ROW COUNTS VERIFICATION
SELECT 'users'       AS tbl, COUNT(*) FROM users
UNION ALL SELECT 'restaurants', COUNT(*) FROM restaurants
UNION ALL SELECT 'menu',        COUNT(*) FROM menu
UNION ALL SELECT 'orders',      COUNT(*) FROM orders
UNION ALL SELECT 'reviews',     COUNT(*) FROM reviews
UNION ALL SELECT 'delivery',    COUNT(*) FROM delivery;
