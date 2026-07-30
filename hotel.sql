-- Hotel Management System Database Script
-- College DBMS Mini Project
-- Database: hotel_management

-- Create the database if it doesn't exist
CREATE DATABASE IF NOT EXISTS hotel_management;
USE hotel_management;

-- Drop tables in proper order (respecting foreign key dependencies)
DROP TABLE IF EXISTS bookings;
DROP TABLE IF EXISTS employees;
DROP TABLE IF EXISTS rooms;
DROP TABLE IF EXISTS customers;

-- 1. Customers Table
CREATE TABLE customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(15) NOT NULL
);

-- 2. Rooms Table
CREATE TABLE rooms (
    room_number VARCHAR(10) PRIMARY KEY,
    room_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'Available'
);

-- 3. Bookings Table
CREATE TABLE bookings (
    booking_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    room_number VARCHAR(10) NOT NULL,
    check_in DATE NOT NULL,
    check_out DATE NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (room_number) REFERENCES rooms(room_number) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 4. Employees Table
CREATE TABLE employees (
    employee_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    role VARCHAR(50) NOT NULL,
    phone VARCHAR(15) NOT NULL
);

-- Insert Sample Records

-- Insert Customers
INSERT INTO customers (name, phone) VALUES
('John Doe', '9876543210'),
('Alice Smith', '8765432109'),
('Bob Johnson', '7654321098'),
('Charlie Brown', '6543210987');

-- Insert Rooms
INSERT INTO rooms (room_number, room_type, status) VALUES
('101', 'Single', 'Available'),
('102', 'Single', 'Booked'),
('201', 'Double', 'Available'),
('202', 'Double', 'Booked'),
('301', 'Suite', 'Available'),
('302', 'Suite', 'Available');

-- Insert Employees
INSERT INTO employees (name, role, phone) VALUES
('David Miller', 'Manager', '9998887776'),
('Emma Wilson', 'Receptionist', '8887776665'),
('Frank Thomas', 'Housekeeping', '7776665554'),
('Grace Davis', 'Chef', '6665554443');

-- Insert Bookings (Ensuring room status matches)
-- Room 102 booked by Customer 1 (John Doe)
INSERT INTO bookings (customer_id, room_number, check_in, check_out) VALUES
(1, '102', '2026-07-28', '2026-08-01');

-- Room 202 booked by Customer 2 (Alice Smith)
INSERT INTO bookings (customer_id, room_number, check_in, check_out) VALUES
(2, '202', '2026-07-29', '2026-08-03');
