-- ============================================================
--  Smart Canteen Pre-Order System  –  Database Setup
-- ============================================================
CREATE DATABASE IF NOT EXISTS smart_canteen CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE smart_canteen;

-- ─── USERS ───────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    roll_number VARCHAR(50)  NOT NULL UNIQUE,
    email       VARCHAR(150) NOT NULL UNIQUE,
    password    VARCHAR(255) NOT NULL,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ─── ADMIN ───────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS admin (
    id        INT AUTO_INCREMENT PRIMARY KEY,
    username  VARCHAR(100) NOT NULL UNIQUE,
    password  VARCHAR(255) NOT NULL
);

-- ─── FOOD ITEMS ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS food_items (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    name         VARCHAR(150) NOT NULL,
    description  TEXT,
    price        DECIMAL(8,2) NOT NULL,
    category     ENUM('Breakfast','Meals','Snacks','Drinks') NOT NULL,
    image_url    VARCHAR(255),
    is_available TINYINT(1) DEFAULT 1,
    created_at   DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ─── ORDERS ──────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS orders (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    order_id    VARCHAR(20)  NOT NULL UNIQUE,
    user_id     INT NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    pickup_time VARCHAR(20)  NOT NULL,
    status      ENUM('Pending','Accepted','Preparing','Ready','Completed','Cancelled') DEFAULT 'Pending',
    prep_time   VARCHAR(30),
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ─── ORDER ITEMS ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS order_items (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    order_id     VARCHAR(20) NOT NULL,
    food_item_id INT NOT NULL,
    quantity     INT NOT NULL DEFAULT 1,
    unit_price   DECIMAL(8,2) NOT NULL,
    FOREIGN KEY (order_id)     REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (food_item_id) REFERENCES food_items(id)  ON DELETE CASCADE
);

-- ─── SAMPLE FOOD ITEMS ───────────────────────────────────────
INSERT IGNORE INTO food_items (name, description, price, category, image_url, is_available) VALUES
('Masala Dosa',    'Crispy dosa filled with spiced potato masala, served with coconut chutney & sambar', 35.00,  'Breakfast', 'dosa.jpg',        1),
('Idli Sambar',    '3 soft steamed idlis served with hot sambar and 2 chutneys',                          25.00,  'Breakfast', 'idli.jpg',        1),
('Poha',           'Flattened rice cooked with onions, peas, peanuts and Indian spices',                  20.00,  'Breakfast', 'poha.jpg',        1),
('Upma',           'Semolina porridge tempered with mustard, curry leaves and vegetables',                20.00,  'Breakfast', 'upma.jpg',        1),
('Veg Thali',      'Full meal with rice, 2 rotis, dal, 2 sabzis, raita, pickle & dessert',               80.00,  'Meals',     'thali.jpg',       1),
('Chicken Biryani','Aromatic basmati rice cooked with tender chicken and whole spices',                   110.00, 'Meals',     'biryani.jpg',     1),
('Paneer Rice',    'Basmati rice sauteed with paneer cubes and mixed vegetables',                         70.00,  'Meals',     'paneer_rice.jpg', 1),
('Chole Bhature',  'Spicy chickpea curry served with 2 fluffy fried bhature',                             60.00,  'Meals',     'chole.jpg',       1),
('Samosa',         '2 crispy pastry pockets stuffed with spiced potatoes & peas, with chutneys',         20.00,  'Snacks',    'samosa.jpg',      1),
('Vada Pav',       'Mumbai street-style spiced potato fritter in a soft bun with chutneys',              15.00,  'Snacks',    'vada_pav.jpg',    1),
('Bhel Puri',      'Puffed rice mixed with veggies, chutneys & sev - a tangy street snack',              25.00,  'Snacks',    'bhel.jpg',        1),
('Bread Pakora',   'Thick bread slices dipped in spiced gram-flour batter and deep fried',               30.00,  'Snacks',    'pakora.jpg',      1),
('Cold Coffee',    'Chilled blended coffee with milk and ice cream, topped with whipped cream',           50.00,  'Drinks',    'coffee.jpg',      1),
('Mango Lassi',    'Thick sweet lassi blended with fresh Alphonso mango pulp',                            40.00,  'Drinks',    'lassi.jpg',       1),
('Masala Chai',    'Strong Indian spiced tea brewed with ginger, cardamom and milk',                      15.00,  'Drinks',    'chai.jpg',        1),
('Fresh Lime Soda','Freshly squeezed lime soda - sweet, salted or both',                                 25.00,  'Drinks',    'lime_soda.jpg',   1);



select * from orders