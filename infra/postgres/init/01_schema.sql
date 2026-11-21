-- Olist Data Warehouse schema (PostgreSQL)

CREATE SCHEMA IF NOT EXISTS dw;

-- Dimension: Date
CREATE TABLE IF NOT EXISTS dw.dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date DATE NOT NULL,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    day INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    day_name VARCHAR(20) NOT NULL,
    is_weekend BOOLEAN NOT NULL
);

-- Dimension: Customer
CREATE TABLE IF NOT EXISTS dw.dim_customer (
    customer_key SERIAL PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL UNIQUE,
    customer_unique_id VARCHAR(50) NOT NULL,
    customer_zip_code_prefix INTEGER,
    customer_city VARCHAR(100),
    customer_state VARCHAR(10)
);

-- Dimension: Seller
CREATE TABLE IF NOT EXISTS dw.dim_seller (
    seller_key SERIAL PRIMARY KEY,
    seller_id VARCHAR(50) NOT NULL UNIQUE,
    seller_zip_code_prefix INTEGER,
    seller_city VARCHAR(100),
    seller_state VARCHAR(10)
);

-- Dimension: Product
CREATE TABLE IF NOT EXISTS dw.dim_product (
    product_key SERIAL PRIMARY KEY,
    product_id VARCHAR(50) NOT NULL UNIQUE,
    product_category_name VARCHAR(100),
    product_category_name_english VARCHAR(100),
    product_weight_g DOUBLE PRECISION,
    product_length_cm DOUBLE PRECISION,
    product_height_cm DOUBLE PRECISION,
    product_width_cm DOUBLE PRECISION
);

-- Fact: Order Items (sales)
CREATE TABLE IF NOT EXISTS dw.fact_order_items (
    order_item_key BIGSERIAL PRIMARY KEY,
    order_id VARCHAR(50) NOT NULL,
    order_item_id INTEGER NOT NULL,
    customer_key INTEGER REFERENCES dw.dim_customer(customer_key),
    product_key INTEGER REFERENCES dw.dim_product(product_key),
    seller_key INTEGER REFERENCES dw.dim_seller(seller_key),
    purchase_date_key INTEGER REFERENCES dw.dim_date(date_key),
    price NUMERIC(12,2) NOT NULL,
    freight_value NUMERIC(12,2) NOT NULL,
    total_item_value NUMERIC(12,2) NOT NULL
);

-- Fact: Orders (order lifecycle)
CREATE TABLE IF NOT EXISTS dw.fact_orders (
    order_key BIGSERIAL PRIMARY KEY,
    order_id VARCHAR(50) NOT NULL UNIQUE,
    customer_key INTEGER REFERENCES dw.dim_customer(customer_key),
    purchase_date_key INTEGER REFERENCES dw.dim_date(date_key),
    order_status VARCHAR(30) NOT NULL,
    approved_at TIMESTAMP,
    delivered_customer_at TIMESTAMP,
    estimated_delivery_at TIMESTAMP,
    delivery_days INTEGER,
    is_late BOOLEAN,
    review_score INTEGER,
    total_payment_value NUMERIC(12,2),
    payment_type VARCHAR(30)
);