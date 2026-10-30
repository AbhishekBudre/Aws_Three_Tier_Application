CREATE TABLE IF NOT EXISTS inventory (
 id SERIAL PRIMARY KEY,
 product_name VARCHAR(150) NOT NULL,
 category VARCHAR(100) NOT NULL,
 quantity INTEGER NOT NULL DEFAULT 0 CHECK (quantity >= 0),
 price NUMERIC(10, 2) NOT NULL DEFAULT 0 CHECK (price >= 0),
 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
 );

 INSERT INTO inventory (product_name, category, quantity, price)
 VALUES
 ('Laptop', 'Electronics', 10, 55000.00),
 ('Keyboard', 'Accessories', 25, 1200.00),
 ('Monitor', 'Electronics', 8, 12500.00)
 ON CONFLICT DO NOTHING;