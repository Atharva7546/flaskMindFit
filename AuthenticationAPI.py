from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from flask_mysqldb import MySQL
import re

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'demo'
mysql = MySQL(app)

def is_valid_email(email):
    email_regex = r'^[\w\-.]+@[a-zA-Z0-9]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email)

def is_existing_user(email):
    cur = mysql.connection.cursor()
    cur.execute("SELECT email FROM login WHERE email = %s", (email,))
    user = cur.fetchone()
    cur.close()
    return user is not None

def register_user(email, password, gender, name):
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO login (email, password, gender, name) VALUES (%s, %s, %s, %s)", (email, hashed_password, gender, name))
    mysql.connection.commit()
    cur.close()

def verify_login(email, password):
    cur = mysql.connection.cursor()
    cur.execute("SELECT password FROM login WHERE email = %s", (email,))
    stored_password = cur.fetchone()
    cur.close()
    return stored_password[0] if stored_password else None

def sanitize_input(input_str):
    return input_str.strip() if isinstance(input_str, str) else input_str

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email, password, gender, name = sanitize_input(data.get('email')), sanitize_input(data.get('password')), sanitize_input(data.get('gender')), sanitize_input(data.get('name'))

    if not all((email, password, gender, name)):
        return jsonify({'message': 'Please provide all required fields: email, password, gender, name'}), 400

    if not is_valid_email(email):
        return jsonify({'message': 'Invalid email format'}), 400

    if len(password) < 8:
        return jsonify({'message': 'Password should be at least 8 characters long'}), 400

    if gender not in ['male', 'female', 'other']:
        return jsonify({'message': 'Invalid gender. Allowed values are: male, female, other'}), 400

    if is_existing_user(email):
        return jsonify({'message': 'User with this email already exists'}), 400

    try:
        register_user(email, password, gender, name)
        return jsonify({'message': 'Registration successful'}), 201

    except Exception as e:
        return jsonify({'message': 'An error occurred: {}'.format(str(e))}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email, password = sanitize_input(data.get('email')), sanitize_input(data.get('password'))

    if not all((email, password)):
        return jsonify({'message': 'Please provide both email and password'}), 400

    if not is_valid_email(email):
        return jsonify({'message': 'Invalid email format'}), 400

    stored_password = verify_login(email, password)

    if stored_password is None or not bcrypt.check_password_hash(stored_password, password):
        return jsonify({'message': 'Invalid email or password'}), 401

    return jsonify({'message': 'Login successful'}), 200


def get_user_details(email):
    cur = mysql.connection.cursor()
    cur.execute("SELECT name, email, gender FROM login WHERE email = %s", (email,))
    user_details = cur.fetchone()
    cur.close()
    if user_details:
        return {
            'name': user_details[0],
            'email': user_details[1],
            'gender': user_details[2]
        }
    return None

@app.route('/getdetails', methods=['GET'])
def get_user():
    email = request.args.get('email')

    if not email or not is_valid_email(email):
        return jsonify({'message': 'Please provide a valid email'}), 400

    user_details = get_user_details(email)
    if user_details:
        return jsonify(user_details), 200
    else:
        return jsonify({'message': 'User not found'}), 404



if __name__ == '__main__':
    app.run(host='192.168.1.6')