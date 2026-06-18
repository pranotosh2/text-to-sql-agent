-- Northwind sample database (simplified)
-- Run this once to populate PostgreSQL with real data

CREATE TABLE IF NOT EXISTS categories (
    category_id   SERIAL PRIMARY KEY,
    category_name VARCHAR(50) NOT NULL,
    description   TEXT
);

CREATE TABLE IF NOT EXISTS suppliers (
    supplier_id   SERIAL PRIMARY KEY,
    company_name  VARCHAR(100) NOT NULL,
    contact_name  VARCHAR(100),
    country       VARCHAR(50),
    phone         VARCHAR(30)
);

CREATE TABLE IF NOT EXISTS products (
    product_id        SERIAL PRIMARY KEY,
    product_name      VARCHAR(100) NOT NULL,
    supplier_id       INTEGER REFERENCES suppliers(supplier_id),
    category_id       INTEGER REFERENCES categories(category_id),
    unit_price        NUMERIC(10,2) DEFAULT 0,
    units_in_stock    INTEGER DEFAULT 0,
    units_on_order    INTEGER DEFAULT 0,
    reorder_level     INTEGER DEFAULT 0,
    discontinued      BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS customers (
    customer_id   CHAR(5) PRIMARY KEY,
    company_name  VARCHAR(100) NOT NULL,
    contact_name  VARCHAR(100),
    city          VARCHAR(50),
    country       VARCHAR(50),
    phone         VARCHAR(30)
);

CREATE TABLE IF NOT EXISTS employees (
    employee_id   SERIAL PRIMARY KEY,
    first_name    VARCHAR(50) NOT NULL,
    last_name     VARCHAR(50) NOT NULL,
    title         VARCHAR(100),
    hire_date     DATE,
    country       VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS orders (
    order_id      SERIAL PRIMARY KEY,
    customer_id   CHAR(5) REFERENCES customers(customer_id),
    employee_id   INTEGER REFERENCES employees(employee_id),
    order_date    DATE,
    shipped_date  DATE,
    ship_country  VARCHAR(50),
    freight       NUMERIC(10,2) DEFAULT 0
);

CREATE TABLE IF NOT EXISTS order_details (
    order_id    INTEGER REFERENCES orders(order_id),
    product_id  INTEGER REFERENCES products(product_id),
    unit_price  NUMERIC(10,2) NOT NULL,
    quantity    SMALLINT NOT NULL,
    discount    REAL DEFAULT 0,
    PRIMARY KEY (order_id, product_id)
);

-- ── Seed data ─────────────────────────────────────────────────────────────────

INSERT INTO categories (category_name, description) VALUES
('Beverages',    'Soft drinks, coffees, teas, beers'),
('Condiments',   'Sweet and savory sauces, relishes, spreads'),
('Confections',  'Desserts, candies, and sweet breads'),
('Dairy Products','Cheeses'),
('Grains/Cereals','Breads, crackers, pasta, cereal'),
('Meat/Poultry', 'Prepared meats'),
('Produce',      'Dried fruit and bean curd'),
('Seafood',      'Seaweed and fish')
ON CONFLICT DO NOTHING;

INSERT INTO suppliers (company_name, contact_name, country, phone) VALUES
('Exotic Liquids',          'Charlotte Cooper',  'UK',      '(171) 555-2222'),
('New Orleans Cajun Delights','Shelley Burke',   'USA',     '(100) 555-4822'),
('Grandma Kelly''s Homestead','Regina Murphy',  'USA',     '(313) 555-5735'),
('Tokyo Traders',            'Yoshi Nagase',    'Japan',   '(03) 3555-5011'),
('Cooperativa de Quesos',    'Antonio del Valle','Spain',  '(98) 598 76 54')
ON CONFLICT DO NOTHING;

INSERT INTO products (product_name, supplier_id, category_id, unit_price, units_in_stock, units_on_order, reorder_level, discontinued) VALUES
('Chai',              1, 1, 18.00,  39, 0, 10, FALSE),
('Chang',             1, 1, 19.00,  17, 40, 25, FALSE),
('Aniseed Syrup',     1, 2, 10.00,  13, 70, 25, FALSE),
('Chef Anton''s Cajun Seasoning', 2, 2, 22.00, 53, 0, 0, FALSE),
('Grandma''s Boysenberry Spread', 3, 2, 25.00, 120, 0, 25, FALSE),
('Uncle Bob''s Organic Dried Pears', 3, 7, 30.00, 15, 0, 10, FALSE),
('Northwoods Cranberry Sauce', 3, 2, 40.00, 6, 0, 0, FALSE),
('Mishi Kobe Niku',   4, 6, 97.00,  29, 0, 0, TRUE),
('Ikura',             4, 8, 31.00,  31, 0, 0, FALSE),
('Queso Cabrales',    5, 4, 21.00,  22, 30, 30, FALSE),
('Queso Manchego La Pastora', 5, 4, 38.00, 86, 0, 0, FALSE),
('Konbu',             4, 8, 6.00,   24, 0, 5, FALSE),
('Tofu',              4, 7, 23.25,  35, 0, 0, FALSE),
('Genen Shouyu',      4, 2, 15.50,  39, 0, 5, FALSE),
('Pavlova',           3, 3, 17.45, 29, 0, 10, FALSE)
ON CONFLICT DO NOTHING;

INSERT INTO customers (customer_id, company_name, contact_name, city, country, phone) VALUES
('ALFKI', 'Alfreds Futterkiste',       'Maria Anders',   'Berlin',    'Germany', '030-0074321'),
('ANATR', 'Ana Trujillo Emparedados',  'Ana Trujillo',   'México D.F.','Mexico', '(5) 555-4729'),
('ANTON', 'Antonio Moreno Taquería',   'Antonio Moreno', 'México D.F.','Mexico', '(5) 555-3932'),
('AROUT', 'Around the Horn',           'Thomas Hardy',   'London',    'UK',      '(171) 555-7788'),
('BERGS', 'Berglunds snabbköp',        'Christina Berglund','Luleå', 'Sweden',  '0921-12 34 65'),
('BLAUS', 'Blauer See Delikatessen',   'Hanna Moos',     'Mannheim',  'Germany', '0621-08460'),
('BLONP', 'Blondel père et fils',      'Frédérique Citeaux','Strasbourg','France','88.60.15.31'),
('BOLID', 'Bólido Comidas preparadas', 'Martín Sommer',  'Madrid',    'Spain',   '(91) 555 22 82'),
('BONAP', 'Bon app''',                 'Laurence Lebihan','Marseille', 'France',  '91.24.45.40'),
('BOTTM', 'Bottom-Dollar Markets',     'Elizabeth Lincoln','Tsawassen','Canada','(604) 555-4729'),
('BSBEV', 'B''s Beverages',            'Victoria Ashworth','London',  'UK',      '(171) 555-1212'),
('CACTU', 'Cactus Comidas para llevar','Patricio Simpson','Buenos Aires','Argentina','(1) 135-5555'),
('CENTC', 'Centro comercial Moctezuma','Francisco Chang','México D.F.','Mexico', '(5) 555-3392'),
('CHOPS', 'Chop-suey Chinese',         'Yang Wang',      'Bern',      'Switzerland','0452-076545'),
('COMMI', 'Comércio Mineiro',          'Pedro Afonso',   'Sao Paulo', 'Brazil',  '(11) 555-7647')
ON CONFLICT DO NOTHING;

INSERT INTO employees (first_name, last_name, title, hire_date, country) VALUES
('Nancy',   'Davolio',   'Sales Representative',      '1992-05-01', 'USA'),
('Andrew',  'Fuller',    'Vice President Sales',       '1992-08-14', 'USA'),
('Janet',   'Leverling', 'Sales Representative',      '1992-04-01', 'USA'),
('Margaret','Peacock',   'Sales Representative',      '1993-05-03', 'USA'),
('Steven',  'Buchanan',  'Sales Manager',             '1993-10-17', 'UK'),
('Michael', 'Suyama',    'Sales Representative',      '1993-10-17', 'UK'),
('Robert',  'King',      'Sales Representative',      '1994-01-02', 'UK'),
('Laura',   'Callahan',  'Inside Sales Coordinator',  '1994-03-05', 'USA'),
('Anne',    'Dodsworth', 'Sales Representative',      '1994-11-15', 'UK')
ON CONFLICT DO NOTHING;

INSERT INTO orders (customer_id, employee_id, order_date, shipped_date, ship_country, freight) VALUES
('ALFKI', 6, '1997-08-25', '1997-09-02', 'Germany',  29.46),
('ALFKI', 1, '1997-10-03', '1997-10-13', 'Germany',  61.02),
('ALFKI', 4, '1997-10-13', '1997-10-21', 'Germany',   2.26),
('ALFKI', 4, '1998-01-15', '1998-01-21', 'Germany',  69.53),
('ANATR', 3, '1996-09-18', '1996-09-24', 'Mexico',   43.90),
('ANATR', 1, '1997-08-08', '1997-08-14', 'Mexico',   13.97),
('AROUT', 4, '1996-11-14', '1996-11-21', 'UK',       10.29),
('AROUT', 1, '1997-07-31', '1997-08-07', 'UK',        1.35),
('BERGS', 8, '1996-08-12', '1996-08-16', 'Sweden',  133.96),
('BERGS', 2, '1997-04-25', '1997-05-05', 'Sweden',    0.00),
('BLAUS', 3, '1997-04-09', '1997-04-15', 'Germany',   8.93),
('BONAP', 5, '1996-10-16', '1996-10-22', 'France',   10.21),
('BONAP', 2, '1997-11-11', '1997-11-17', 'France',   55.28),
('BOTTM', 1, '1996-12-03', '1996-12-10', 'Canada',   24.69),
('BSBEV', 6, '1997-09-02', '1997-09-08', 'UK',        3.04),
('CHOPS', 4, '1997-03-20', '1997-03-27', 'Switzerland',75.89),
('COMMI', 7, '1997-11-19', '1997-11-25', 'Brazil',   11.61)
ON CONFLICT DO NOTHING;

INSERT INTO order_details (order_id, product_id, unit_price, quantity, discount) VALUES
(1,  11, 14.00, 12, 0.0),
(1,  42, 9.80,  10, 0.0),
(1,  72, 34.80, 5,  0.0),
(2,  14, 23.25, 9,  0.0),
(2,  51, 42.40, 40, 0.2),
(2,  65, 16.80, 10, 0.2),
(3,   7, 30.00, 6,  0.0),
(4,  72, 34.80, 8,  0.0),
(5,  46, 12.00, 10, 0.0),
(5,  53, 26.20, 10, 0.0),
(6,  76, 18.00, 9,  0.0),
(7,   1, 14.40, 45, 0.25),
(8,   3,  8.00, 10, 0.0),
(8,  13, 6.00,  35, 0.0),
(9,  14, 18.60, 10, 0.0),
(10,  4, 17.60, 1,  0.0),
(10,  6, 25.00, 15, 0.05),
(11, 10, 31.00, 30, 0.0),
(12,  2, 15.20, 15, 0.0),
(13,  9, 97.00, 25, 0.05),
(14,  5, 21.35, 12, 0.0),
(15, 11, 16.80, 7,  0.0),
(16, 15, 13.96, 20, 0.0),
(17, 13, 6.00,  6,  0.0)
ON CONFLICT DO NOTHING;
