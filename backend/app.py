from flask import Flask, request, jsonify, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import os

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app, resources={r"/api/*": {"origins": "*"}})
app.secret_key = os.urandom(24)

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Ansh@2020',  # Replace with your MySQL password
    'database': 'quickserve'
}

def get_db():
    try:
        return mysql.connector.connect(**db_config)
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(255) UNIQUE,
            password VARCHAR(255),
            name VARCHAR(255),
            user_type VARCHAR(50)
        )
    ''')

    # Create services table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS services (
            id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
            pro_id INT UNSIGNED,
            service_type VARCHAR(100),
            description TEXT,
            hourly_rate DECIMAL(10,2),
            FOREIGN KEY (pro_id) REFERENCES users(id)
        )
    ''')

    # Create requests table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS requests (
            id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
            user_id INT UNSIGNED,
            service_id INT UNSIGNED,
            status VARCHAR(50),
            description TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (service_id) REFERENCES services(id)
        )
    ''')

    conn.commit()
    cursor.close()
    conn.close()

@app.before_request
def setup():
    init_db()

@app.route('/')
def serve_static():
    return app.send_static_file('index.html')

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    if not all(field in data for field in ['email', 'password', 'name', 'user_type']):
        return jsonify({'error': 'Missing required fields'}), 400

    conn = get_db()
    cursor = conn.cursor()

    try:
        hashed_password = generate_password_hash(data['password'])
        cursor.execute('''
            INSERT INTO users (email, password, name, user_type)
            VALUES (%s, %s, %s, %s)
        ''', (data['email'], hashed_password, data['name'], data['user_type']))
        conn.commit()
        user_id = cursor.lastrowid
        return jsonify({'id': user_id, 'message': 'Registration successful'}), 201
    except mysql.connector.IntegrityError:
        return jsonify({'error': 'Email already exists'}), 400
    finally:
        cursor.close()
        conn.close()

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    if 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Missing required fields'}), 400

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute('SELECT * FROM users WHERE email = %s', (data['email'],))
        user = cursor.fetchone()

        if user and check_password_hash(user['password'], data['password']):
            session['user_id'] = user['id']
            return jsonify({
                'id': user['id'],
                'email': user['email'],
                'name': user['name'],
                'user_type': user['user_type']
            })
        return jsonify({'error': 'Invalid credentials'}), 401
    finally:
        cursor.close()
        conn.close()

@app.route('/api/services', methods=['GET', 'POST'])
def services():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    try:
        if request.method == 'GET':
            cursor.execute('SELECT * FROM services')
            services = cursor.fetchall()
            return jsonify(services)

        if request.method == 'POST' and session.get('user_id'):
            data = request.json
            cursor.execute('''
                INSERT INTO services (pro_id, service_type, description, hourly_rate)
                VALUES (%s, %s, %s, %s)
            ''', (session['user_id'], data['service_type'], data['description'], data['hourly_rate']))
            conn.commit()
            return jsonify({'id': cursor.lastrowid, 'message': 'Service added successfully'}), 201
        return jsonify({'error': 'Unauthorized'}), 403
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    app.run(debug=True)
