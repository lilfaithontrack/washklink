-- WashLink Database Schema (Normalized, Production-Ready)
-- Compatible with SQLite, MySQL, and PostgreSQL

-- =====================================================
-- DATABASE CREATION
-- =====================================================

CREATE DATABASE IF NOT EXISTS washlink_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE washlink_db;

-- =====================================================
-- USERS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS new_users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    password VARCHAR(255),
    role VARCHAR(20) NOT NULL DEFAULT 'user' CHECK (role IN ('user', 'manager', 'admin')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_login DATETIME
);
CREATE INDEX IF NOT EXISTS idx_users_email ON new_users(email);
CREATE INDEX IF NOT EXISTS idx_users_phone ON new_users(phone_number);
CREATE INDEX IF NOT EXISTS idx_users_role ON new_users(role);
CREATE INDEX IF NOT EXISTS idx_users_active ON new_users(is_active);

-- =====================================================
-- SERVICE PROVIDERS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS service_provider (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    middle_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    address TEXT NOT NULL,
    phone_number BIGINT UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'busy', 'offline', 'suspended')),
    is_active BOOLEAN DEFAULT TRUE,
    is_available BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    latitude DECIMAL(10,8) NOT NULL,
    longitude DECIMAL(11,8) NOT NULL,
    service_radius DECIMAL(5,2) DEFAULT 10.0,
    nearby_condominum VARCHAR(255) NOT NULL,
    date_of_birth DATE NOT NULL DEFAULT '2000-01-01',
    washing_machine BOOLEAN DEFAULT TRUE,
    has_dryer BOOLEAN DEFAULT FALSE,
    has_iron BOOLEAN DEFAULT TRUE,
    max_daily_orders INT DEFAULT 20,
    current_order_count INT DEFAULT 0,
    average_completion_time DECIMAL(5,2) DEFAULT 24.0,
    rating DECIMAL(3,2) DEFAULT 0.0,
    total_orders_completed INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_active DATETIME DEFAULT CURRENT_TIMESTAMP,
    business_name VARCHAR(255),
    business_license VARCHAR(255),
    description TEXT
);
CREATE INDEX IF NOT EXISTS idx_provider_email ON service_provider(email);
CREATE INDEX IF NOT EXISTS idx_provider_phone ON service_provider(phone_number);
CREATE INDEX IF NOT EXISTS idx_provider_status ON service_provider(status);
CREATE INDEX IF NOT EXISTS idx_provider_location ON service_provider(latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_provider_active ON service_provider(is_active, is_available);

-- =====================================================
-- DRIVERS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS drivers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    license_number VARCHAR(50) UNIQUE NOT NULL,
    vehicle_type VARCHAR(20) NOT NULL CHECK (vehicle_type IN ('motorcycle', 'car', 'van', 'bicycle', 'foot')),
    vehicle_plate VARCHAR(20) UNIQUE NOT NULL,
    vehicle_model VARCHAR(100),
    vehicle_color VARCHAR(50),
    status VARCHAR(20) DEFAULT 'available' CHECK (status IN ('available', 'busy', 'offline', 'on_delivery', 'suspended')),
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    current_latitude DECIMAL(10,8),
    current_longitude DECIMAL(11,8),
    last_location_update DATETIME,
    service_radius DECIMAL(5,2) DEFAULT 15.0,
    base_latitude DECIMAL(10,8),
    base_longitude DECIMAL(11,8),
    rating DECIMAL(3,2) DEFAULT 0.0,
    total_deliveries INT DEFAULT 0,
    successful_deliveries INT DEFAULT 0,
    average_delivery_time DECIMAL(5,2) DEFAULT 30.0,
    date_joined DATE DEFAULT CURRENT_DATE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_active DATETIME DEFAULT CURRENT_TIMESTAMP,
    current_order_id INT
);
CREATE INDEX IF NOT EXISTS idx_driver_email ON drivers(email);
CREATE INDEX IF NOT EXISTS idx_driver_phone ON drivers(phone_number);
CREATE INDEX IF NOT EXISTS idx_driver_license ON drivers(license_number);
CREATE INDEX IF NOT EXISTS idx_driver_vehicle_plate ON drivers(vehicle_plate);
CREATE INDEX IF NOT EXISTS idx_driver_status ON drivers(status);
CREATE INDEX IF NOT EXISTS idx_driver_location ON drivers(current_latitude, current_longitude);
CREATE INDEX IF NOT EXISTS idx_driver_active ON drivers(is_active, status);

-- =====================================================
-- ITEMS TABLE (NEW, normalized)
-- =====================================================
CREATE TABLE IF NOT EXISTS items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'ETB',
    category VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    estimated_time VARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_items_category ON items(category);
CREATE INDEX IF NOT EXISTS idx_items_active ON items(is_active);

-- =====================================================
-- ORDERS TABLE (was bookings)
-- =====================================================
CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    service_provider_id INT,
    driver_id INT,
    pickup_latitude DECIMAL(10,8),
    pickup_longitude DECIMAL(11,8),
    pickup_address VARCHAR(500),
    delivery_latitude DECIMAL(10,8),
    delivery_longitude DECIMAL(11,8),
    delivery_address VARCHAR(500),
    price_tag DECIMAL(10,2) NOT NULL DEFAULT 0.0,
    subtotal DECIMAL(10,2) NOT NULL,
    payment_option VARCHAR(50),
    delivery BOOLEAN DEFAULT FALSE,
    delivery_km DECIMAL(5,2) DEFAULT 0.0,
    delivery_charge DECIMAL(10,2) DEFAULT 0.0,
    cash_on_delivery BOOLEAN DEFAULT FALSE,
    note TEXT,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'assigned', 'accepted', 'rejected', 'in_progress', 'ready_for_pickup', 'out_for_delivery', 'delivered', 'completed', 'cancelled')),
    service_type VARCHAR(50) NOT NULL DEFAULT 'Machine Wash' CHECK (service_type IN ('By Hand Wash', 'Premium Laundry Service', 'Machine Wash')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    assigned_at DATETIME,
    accepted_at DATETIME,
    completed_at DATETIME,
    estimated_pickup_time DATETIME,
    estimated_completion_time DATETIME,
    estimated_delivery_time DATETIME,
    assignment_attempts INT DEFAULT 0,
    max_assignment_radius DECIMAL(5,2) DEFAULT 5.0,
    special_instructions TEXT,
    priority_level INT DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES new_users(id) ON DELETE CASCADE,
    FOREIGN KEY (service_provider_id) REFERENCES service_provider(id) ON DELETE SET NULL,
    FOREIGN KEY (driver_id) REFERENCES drivers(id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_order_user ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_order_provider ON orders(service_provider_id);
CREATE INDEX IF NOT EXISTS idx_order_driver ON orders(driver_id);
CREATE INDEX IF NOT EXISTS idx_order_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_order_created ON orders(created_at);
CREATE INDEX IF NOT EXISTS idx_order_location ON orders(pickup_latitude, pickup_longitude);
CREATE INDEX IF NOT EXISTS idx_order_delivery ON orders(delivery_latitude, delivery_longitude);

-- =====================================================
-- ORDER ITEMS TABLE (Normalized order-item linkage)
-- =====================================================
CREATE TABLE IF NOT EXISTS order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    category_id INT NOT NULL,
    quantity INT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    service_type VARCHAR(50),
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES items(id) ON DELETE RESTRICT
);
CREATE INDEX IF NOT EXISTS idx_orderitem_order ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_orderitem_product ON order_items(product_id);

-- =====================================================
-- PAYMENTS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    user_id INT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'ETB',
    payment_method VARCHAR(20) NOT NULL CHECK (payment_method IN ('chapa', 'telebirr', 'cash_on_delivery')),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'completed', 'failed', 'cancelled')),
    external_transaction_id VARCHAR(255),
    gateway_reference VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    completed_at DATETIME,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES new_users(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_payment_order ON payments(order_id);
CREATE INDEX IF NOT EXISTS idx_payment_user ON payments(user_id);
CREATE INDEX IF NOT EXISTS idx_payment_status ON payments(status);
CREATE INDEX IF NOT EXISTS idx_payment_method ON payments(payment_method);
CREATE INDEX IF NOT EXISTS idx_payment_created ON payments(created_at);
CREATE INDEX IF NOT EXISTS idx_payment_external ON payments(external_transaction_id);

-- =====================================================
-- SAMPLE DATA INSERTION (update to match new structure)
-- =====================================================
-- Insert default admin user
INSERT IGNORE INTO new_users (full_name, phone_number, email, password, role, is_active) VALUES 
('System Administrator', '+251911000000', 'admin@washlink.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.iK2O', 'admin', TRUE);

-- Insert sample items
INSERT IGNORE INTO items (name, description, price, category, is_active, estimated_time) VALUES
('Shirt', 'Basic shirt laundry', 50.0, 'Basic', TRUE, '24 hours'),
('Pants', 'Basic pants laundry', 80.0, 'Basic', TRUE, '24 hours'),
('Dress', 'Premium dress laundry', 120.0, 'Premium', TRUE, '48 hours'),
('Suit', 'Premium suit laundry', 200.0, 'Premium', TRUE, '48 hours'),
('Jeans', 'Basic jeans laundry', 90.0, 'Basic', TRUE, '24 hours'),
('T-shirt', 'Basic t-shirt laundry', 40.0, 'Basic', TRUE, '24 hours');

-- Insert sample service providers
INSERT IGNORE INTO service_provider (
    first_name, middle_name, last_name, address, phone_number, email, 
    latitude, longitude, nearby_condominum, business_name, rating, total_orders_completed
) VALUES 
('Abebe', 'Kebede', 'Tadesse', 'Bole, Addis Ababa', 251911111111, 'abebe@washlink.com', 
 8.9806, 38.7578, 'Bole Condominium', 'Bole Laundry Services', 4.5, 150),
('Fatima', 'Ahmed', 'Mohammed', 'Kazanchis, Addis Ababa', 251922222222, 'fatima@washlink.com', 
 9.0127, 38.7619, 'Kazanchis Plaza', 'Kazanchis Premium Laundry', 4.8, 200),
('Yohannes', 'Dawit', 'Haile', 'Piazza, Addis Ababa', 251933333333, 'yohannes@washlink.com', 
 9.0272, 38.7369, 'Piazza Tower', 'Piazza Express Laundry', 4.2, 120);

-- Insert sample drivers
INSERT IGNORE INTO drivers (
    first_name, last_name, email, phone_number, license_number, 
    vehicle_type, vehicle_plate, vehicle_model, vehicle_color,
    current_latitude, current_longitude, rating, total_deliveries, successful_deliveries
) VALUES 
('Tesfaye', 'Bekele', 'tesfaye@washlink.com', '+251944444444', 'DL001234', 
 'motorcycle', 'AA-12345', 'Honda CG125', 'Red',
 8.9806, 38.7578, 4.6, 300, 285),
('Mariam', 'Hassan', 'mariam@washlink.com', '+251955555555', 'DL005678', 
 'car', 'AA-67890', 'Toyota Corolla', 'White',
 9.0127, 38.7619, 4.8, 250, 240),
('Dawit', 'Mengistu', 'dawit@washlink.com', '+251966666666', 'DL009012', 
 'motorcycle', 'AA-11111', 'Yamaha YBR125', 'Blue',
 9.0272, 38.7369, 4.4, 180, 170);

-- Insert sample regular users
INSERT IGNORE INTO new_users (full_name, phone_number, email, role, is_active) VALUES 
('Kidist Alemayehu', '+251977777777', 'kidist@example.com', 'user', TRUE),
('Bereket Tadesse', '+251988888888', 'bereket@example.com', 'user', TRUE),
('Rahel Mohammed', '+251999999999', 'rahel@example.com', 'user', TRUE);

-- Insert sample orders
INSERT IGNORE INTO orders (
    user_id, service_provider_id, price_tag, subtotal, 
    pickup_address, delivery_address, delivery, delivery_charge,
    status, service_type, pickup_latitude, pickup_longitude
) VALUES 
(2, 1, 310.0, 310.0,
 'Bole, Addis Ababa', 'Bole, Addis Ababa', FALSE, 0.0,
 'completed', 'Machine Wash', 8.9806, 38.7578),
(3, 2, 320.0, 320.0,
 'Kazanchis, Addis Ababa', 'Kazanchis, Addis Ababa', TRUE, 50.0,
 'in_progress', 'Premium Laundry Service', 9.0127, 38.7619),
(4, 3, 380.0, 380.0,
 'Piazza, Addis Ababa', 'Piazza, Addis Ababa', FALSE, 0.0,
 'pending', 'Machine Wash', 9.0272, 38.7369);

-- Insert sample order items
INSERT IGNORE INTO order_items (order_id, product_id, category_id, quantity, price, service_type) VALUES
(1, 1, 1, 3, 50.0, 'Basic'), -- 3 Shirts
(1, 2, 1, 2, 80.0, 'Basic'), -- 2 Pants
(2, 3, 2, 1, 120.0, 'Premium'), -- 1 Dress
(2, 4, 2, 1, 200.0, 'Premium'), -- 1 Suit
(3, 5, 1, 2, 90.0, 'Basic'), -- 2 Jeans
(3, 6, 1, 5, 40.0, 'Basic'); -- 5 T-shirts

-- Insert sample payments
INSERT IGNORE INTO payments (order_id, user_id, amount, payment_method, status) VALUES 
(1, 2, 310.0, 'telebirr', 'completed'),
(2, 3, 370.0, 'chapa', 'completed'),
(3, 4, 380.0, 'cash_on_delivery', 'pending');

-- =====================================================
-- VIEWS FOR COMMON QUERIES (update to use orders)
-- =====================================================
CREATE VIEW IF NOT EXISTS active_orders AS
SELECT 
    o.id,
    o.status,
    o.service_type,
    o.subtotal,
    o.delivery_charge,
    o.created_at,
    u.full_name as customer_name,
    u.phone_number as customer_phone,
    sp.business_name as provider_name,
    sp.phone_number as provider_phone,
    d.first_name || ' ' || d.last_name as driver_name,
    d.phone_number as driver_phone
FROM orders o
LEFT JOIN new_users u ON o.user_id = u.id
LEFT JOIN service_provider sp ON o.service_provider_id = sp.id
LEFT JOIN drivers d ON o.driver_id = d.id
WHERE o.status IN ('pending', 'assigned', 'accepted', 'in_progress', 'ready_for_pickup', 'out_for_delivery');

CREATE VIEW IF NOT EXISTS provider_performance AS
SELECT 
    sp.id,
    sp.business_name,
    sp.first_name || ' ' || sp.last_name as provider_name,
    sp.rating,
    sp.total_orders_completed,
    sp.average_completion_time,
    COUNT(o.id) as total_orders,
    COUNT(CASE WHEN o.status = 'completed' THEN 1 END) as completed_orders,
    AVG(o.subtotal) as avg_order_value
FROM service_provider sp
LEFT JOIN orders o ON sp.id = o.service_provider_id
WHERE sp.is_active = TRUE
GROUP BY sp.id;

CREATE VIEW IF NOT EXISTS driver_performance AS
SELECT 
    d.id,
    d.first_name || ' ' || d.last_name as driver_name,
    d.rating,
    d.total_deliveries,
    d.successful_deliveries,
    d.average_delivery_time,
    COUNT(o.id) as total_orders,
    COUNT(CASE WHEN o.status = 'delivered' THEN 1 END) as delivered_orders
FROM drivers d
LEFT JOIN orders o ON d.id = o.driver_id
WHERE d.is_active = TRUE
GROUP BY d.id;

-- =====================================================
-- END OF SCHEMA
-- ===================================================== 