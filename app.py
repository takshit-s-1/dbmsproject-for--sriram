# Hotel Management System Backend (SQLite Version)
# College DBMS Mini Project
# Runs out-of-the-box without needing MySQL installation. Automatically creates the database and seeds sample data.

import os
import sqlite3
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

base_dir = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=base_dir, static_url_path='')
CORS(app)  # Enable CORS for cross-origin frontend testing

DB_PATH = os.path.join(base_dir, 'hotel.db')

def get_db_connection():
    """Establishes connection to the SQLite database and returns dictionary-like rows"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # Enable foreign keys support in SQLite
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    """Automatically creates tables and populates sample records if the database is new"""
    if not os.path.exists(DB_PATH):
        print("Database not found. Creating a new local SQLite database (hotel.db) and seeding sample records...")
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. Customers Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL
            )
        """)
        
        # 2. Rooms Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rooms (
                room_number TEXT PRIMARY KEY,
                room_type TEXT NOT NULL,
                status TEXT DEFAULT 'Available'
            )
        """)
        
        # 3. Bookings Table (with foreign key constraints)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                room_number TEXT NOT NULL,
                check_in TEXT NOT NULL,
                check_out TEXT NOT NULL,
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE,
                FOREIGN KEY (room_number) REFERENCES rooms(room_number) ON DELETE CASCADE
            )
        """)
        
        # 4. Employees Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                role TEXT NOT NULL,
                phone TEXT NOT NULL
            )
        """)
        
        # Seed Customers
        cursor.executemany("INSERT INTO customers (name, phone) VALUES (?, ?)", [
            ('John Doe', '9876543210'),
            ('Alice Smith', '8765432109'),
            ('Bob Johnson', '7654321098'),
            ('Charlie Brown', '6543210987')
        ])
        
        # Seed Rooms
        cursor.executemany("INSERT INTO rooms (room_number, room_type, status) VALUES (?, ?, ?)", [
            ('101', 'Single', 'Available'),
            ('102', 'Single', 'Booked'),
            ('201', 'Double', 'Available'),
            ('202', 'Double', 'Booked'),
            ('301', 'Suite', 'Available'),
            ('302', 'Suite', 'Available')
        ])
        
        # Seed Employees
        cursor.executemany("INSERT INTO employees (name, role, phone) VALUES (?, ?, ?)", [
            ('David Miller', 'Manager', '9998887776'),
            ('Emma Wilson', 'Receptionist', '8887776665'),
            ('Frank Thomas', 'Housekeeping', '7776665554'),
            ('Grace Davis', 'Chef', '6665554443')
        ])
        
        # Seed Bookings
        cursor.executemany("INSERT INTO bookings (customer_id, room_number, check_in, check_out) VALUES (?, ?, ?, ?)", [
            (1, '102', '2026-07-28', '2026-08-01'),
            (2, '202', '2026-07-29', '2026-08-03')
        ])
        
        conn.commit()
        conn.close()
        print("Database initialized successfully!")

# Initialize the SQLite Database
init_db()

# ----------------- Serve Frontend -----------------

@app.route('/')
def serve_index():
    """Serves the index.html frontend page on root access"""
    return send_from_directory(base_dir, 'index.html')

# ----------------- Dashboard Stats -----------------

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard_stats():
    """Fetches total counts and room status metrics for the dashboard cards"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute("SELECT COUNT(*) as count FROM customers")
        total_customers = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM rooms")
        total_rooms = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM rooms WHERE status = 'Available'")
        available_rooms = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM rooms WHERE status = 'Booked'")
        booked_rooms = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM employees")
        total_employees = cursor.fetchone()['count']
        
        connection.close()
        return jsonify({
            'total_customers': total_customers,
            'total_rooms': total_rooms,
            'available_rooms': available_rooms,
            'booked_rooms': booked_rooms,
            'total_employees': total_employees
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ----------------- Customer Management CRUD -----------------

@app.route('/api/customers', methods=['GET'])
def get_customers():
    """Retrieves all customers or filters them based on a search query"""
    search = request.args.get('search', '').strip()
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        if search:
            query = """
                SELECT * FROM customers 
                WHERE name LIKE ? OR phone LIKE ? OR customer_id = ?
            """
            search_pattern = f"%{search}%"
            customer_id_val = int(search) if search.isdigit() else -1
            cursor.execute(query, (search_pattern, search_pattern, customer_id_val))
        else:
            cursor.execute("SELECT * FROM customers")
        
        result = [dict(row) for row in cursor.fetchall()]
        connection.close()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/customers', methods=['POST'])
def add_customer():
    """Creates a new customer record"""
    data = request.json
    name = data.get('name', '').strip()
    phone = data.get('phone', '').strip()
    
    if not name or not phone:
        return jsonify({'error': 'Name and phone fields are required.'}), 400
        
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO customers (name, phone) VALUES (?, ?)", (name, phone))
        connection.commit()
        connection.close()
        return jsonify({'message': 'Customer added successfully!'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/customers/<int:customer_id>', methods=['PUT'])
def edit_customer(customer_id):
    """Updates an existing customer record"""
    data = request.json
    name = data.get('name', '').strip()
    phone = data.get('phone', '').strip()
    
    if not name or not phone:
        return jsonify({'error': 'Name and phone fields are required.'}), 400
        
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("UPDATE customers SET name = ?, phone = ? WHERE customer_id = ?", (name, phone, customer_id))
        connection.commit()
        connection.close()
        return jsonify({'message': 'Customer updated successfully!'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/customers/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    """Deletes a customer. Automatically releases booked rooms back to 'Available' status"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Find any rooms currently booked by this customer and free them up
        cursor.execute("SELECT room_number FROM bookings WHERE customer_id = ?", (customer_id,))
        bookings_to_delete = cursor.fetchall()
        for b in bookings_to_delete:
            cursor.execute("UPDATE rooms SET status = 'Available' WHERE room_number = ?", (b['room_number'],))
        
        # Delete customer (will cascade delete bookings due to FK cascade delete)
        cursor.execute("DELETE FROM customers WHERE customer_id = ?", (customer_id,))
        connection.commit()
        connection.close()
        return jsonify({'message': 'Customer deleted successfully!'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ----------------- Room Management CRUD -----------------

@app.route('/api/rooms', methods=['GET'])
def get_rooms():
    """Retrieves all rooms or filters them based on a search query"""
    search = request.args.get('search', '').strip()
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        if search:
            query = """
                SELECT * FROM rooms 
                WHERE room_number LIKE ? OR room_type LIKE ? OR status LIKE ?
            """
            search_pattern = f"%{search}%"
            cursor.execute(query, (search_pattern, search_pattern, search_pattern))
        else:
            cursor.execute("SELECT * FROM rooms")
            
        result = [dict(row) for row in cursor.fetchall()]
        connection.close()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/rooms', methods=['POST'])
def add_room():
    """Adds a new room record"""
    data = request.json
    room_number = data.get('room_number', '').strip()
    room_type = data.get('room_type', '').strip()
    status = data.get('status', 'Available').strip()
    
    if not room_number or not room_type:
        return jsonify({'error': 'Room number and type are required.'}), 400
        
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Check for duplicate room number
        cursor.execute("SELECT room_number FROM rooms WHERE room_number = ?", (room_number,))
        if cursor.fetchone():
            return jsonify({'error': f'Room number {room_number} already exists.'}), 400
            
        cursor.execute("INSERT INTO rooms (room_number, room_type, status) VALUES (?, ?, ?)", 
                       (room_number, room_type, status))
        connection.commit()
        connection.close()
        return jsonify({'message': 'Room added successfully!'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/rooms/<room_number>', methods=['PUT'])
def edit_room(room_number):
    """Updates an existing room's details"""
    data = request.json
    room_type = data.get('room_type', '').strip()
    status = data.get('status', '').strip()
    
    if not room_type or not status:
        return jsonify({'error': 'Room type and status are required.'}), 400
        
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("UPDATE rooms SET room_type = ?, status = ? WHERE room_number = ?", 
                       (room_type, status, room_number))
        connection.commit()
        connection.close()
        return jsonify({'message': 'Room updated successfully!'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/rooms/<room_number>', methods=['DELETE'])
def delete_room(room_number):
    """Deletes a room record"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM rooms WHERE room_number = ?", (room_number,))
        connection.commit()
        connection.close()
        return jsonify({'message': 'Room deleted successfully!'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ----------------- Booking Management CRUD -----------------

@app.route('/api/bookings', methods=['GET'])
def get_bookings():
    """Retrieves all bookings with customer and room type information"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        query = """
            SELECT b.booking_id, b.customer_id, b.room_number, b.check_in, b.check_out,
                   c.name AS customer_name, c.phone AS customer_phone,
                   r.room_type
            FROM bookings b
            JOIN customers c ON b.customer_id = c.customer_id
            JOIN rooms r ON b.room_number = r.room_number
            ORDER BY b.booking_id DESC
        """
        cursor.execute(query)
        result = [dict(row) for row in cursor.fetchall()]
        connection.close()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/bookings', methods=['POST'])
def book_room():
    """Books a room for a customer and automatically flips the room status to 'Booked'"""
    data = request.json
    customer_id = data.get('customer_id')
    room_number = data.get('room_number')
    check_in = data.get('check_in')
    check_out = data.get('check_out')
    
    if not customer_id or not room_number or not check_in or not check_out:
        return jsonify({'error': 'All booking fields are required.'}), 400
        
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # 1. Verify if room is available
        cursor.execute("SELECT status FROM rooms WHERE room_number = ?", (room_number,))
        room = cursor.fetchone()
        if not room:
            return jsonify({'error': 'Room does not exist.'}), 404
        if room['status'] != 'Available':
            return jsonify({'error': 'Selected room is already booked/unavailable.'}), 400
            
        # 2. Insert booking
        cursor.execute(
            "INSERT INTO bookings (customer_id, room_number, check_in, check_out) VALUES (?, ?, ?, ?)",
            (customer_id, room_number, check_in, check_out)
        )
        # 3. Mark room status as 'Booked'
        cursor.execute("UPDATE rooms SET status = 'Booked' WHERE room_number = ?", (room_number,))
        connection.commit()
        connection.close()
        return jsonify({'message': 'Booking completed successfully and room marked as Booked!'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/bookings/<int:booking_id>', methods=['DELETE'])
def cancel_booking(booking_id):
    """Cancels a booking and automatically flips the room status back to 'Available'"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Find the room number for this booking before deleting
        cursor.execute("SELECT room_number FROM bookings WHERE booking_id = ?", (booking_id,))
        booking = cursor.fetchone()
        if not booking:
            return jsonify({'error': 'Booking not found.'}), 404
            
        room_number = booking['room_number']
        
        # Delete the booking
        cursor.execute("DELETE FROM bookings WHERE booking_id = ?", (booking_id,))
        # Revert room status to 'Available'
        cursor.execute("UPDATE rooms SET status = 'Available' WHERE room_number = ?", (room_number,))
        connection.commit()
        connection.close()
        return jsonify({'message': 'Booking cancelled successfully and room is now Available!'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ----------------- Employee Management CRUD -----------------

@app.route('/api/employees', methods=['GET'])
def get_employees():
    """Retrieves all employee records"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM employees")
        result = [dict(row) for row in cursor.fetchall()]
        connection.close()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/employees', methods=['POST'])
def add_employee():
    """Adds a new employee record"""
    data = request.json
    name = data.get('name', '').strip()
    role = data.get('role', '').strip()
    phone = data.get('phone', '').strip()
    
    if not name or not role or not phone:
        return jsonify({'error': 'Name, role, and phone are required.'}), 400
        
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO employees (name, role, phone) VALUES (?, ?, ?)", (name, role, phone))
        connection.commit()
        connection.close()
        return jsonify({'message': 'Employee record created!'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/employees/<int:employee_id>', methods=['PUT'])
def edit_employee(employee_id):
    """Updates an existing employee record"""
    data = request.json
    name = data.get('name', '').strip()
    role = data.get('role', '').strip()
    phone = data.get('phone', '').strip()
    
    if not name or not role or not phone:
        return jsonify({'error': 'Name, role, and phone are required.'}), 400
        
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE employees SET name = ?, role = ?, phone = ? WHERE employee_id = ?",
            (name, role, phone, employee_id)
        )
        connection.commit()
        connection.close()
        return jsonify({'message': 'Employee details updated!'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/employees/<int:employee_id>', methods=['DELETE'])
def delete_employee(employee_id):
    """Deletes an employee record"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM employees WHERE employee_id = ?", (employee_id,))
        connection.commit()
        connection.close()
        return jsonify({'message': 'Employee deleted successfully!'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting Hotel Management System Flask Server at http://127.0.0.1:5000...")
    app.run(host='127.0.0.1', port=5000, debug=True)
