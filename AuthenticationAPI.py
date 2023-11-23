from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from flask_mysqldb import MySQL
import re
from PIL import Image
import io
import base64
from tensorflow.keras.models import load_model
# from sklearn.preprocessing import StandardScaler, LabelEncoder
import pickle

import numpy as np

model = load_model('model.h5')

label_encoders=[]

with open('encoders.pickle','rb') as f:
    label_encoders=pickle.load(f)

with open('scaler.pickle','rb') as f:
    sc=pickle.load(f)
    
# for le in label_encoders:
#     print(le.classes_)
# exit()

# sc = StandardScaler()
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


def fetch_questions():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, question, option1, option2, option3, option4, option5 FROM data")
        questions_data = cur.fetchall()
        cur.close()

        if not questions_data:
            return {'message': 'No questions found'}, 404

        questions_list = []
        for question_data in questions_data:
            question = {
                'id': question_data[0],
                'question': question_data[1],
                'options': [option for option in question_data[2:] if option]  # Exclude empty options
            }
            questions_list.append(question)

        return questions_list

    except mysql.connection.Error as e:
        return {'message': f"Database error: {str(e)}"}, 500

    except Exception as e:
        return {'message': f"An error occurred: {str(e)}"}, 500

# Route to fetch and display questions and options
@app.route('/fetch_questions', methods=['GET'])
def display_questions():
    questions = fetch_questions()

    if isinstance(questions, list):
        return jsonify({'questions': questions}), 200
    else:
        return jsonify(questions), 500


def save_image_to_db(image_data):
    try:
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO images (image_data) VALUES (%s)", (image_data,))
        mysql.connection.commit()
        cur.close()
        return True
    except Exception as e:
        return False

# Function to fetch image data from the database
def get_image_from_db(image_id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT image_data FROM images WHERE id = %s", (image_id,))
        image_data = cur.fetchone()
        cur.close()
        return image_data[0] if image_data else None
    except Exception as e:
        return None

# Endpoint to upload an image to the database
@app.route('/upload_image', methods=['POST'])
def upload_image():
    if 'image_data' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    image = request.files['image_data']
    image_data = image.read()

    if save_image_to_db(image_data):
        return jsonify({'message': 'Image uploaded successfully'}), 201
    else:
        return jsonify({'error': 'Failed to upload image'}), 500

# Endpoint to fetch and display the image from the database
@app.route('/get_image/<int:image_id>', methods=['GET'])
def get_image(image_id):
    image_data = get_image_from_db(image_id)

    # image = Image.open(io.BytesIO(image_data))
    # image_data = image.resize((100, 100), Image)
    # image.show()

    if image_data:
        # image_data_base64 = base64.b64encode(image_data).decode('utf-8')
        # return jsonify({'image_data': image_data_base64}), 200
        # return jsonify({'image_data': image_data}), 200
        return image_data, 200, {'Content-Type': 'image/png'}
        
        
    else:
        return jsonify({'error': 'Image not found'}), 404
    
@app.route('/evaluate', methods=['POST'])
def evaluate():
    answers=request.get_json()
    print(answers)
    X=np.zeros((1,30))
    i=0
    for answer in answers:
        print(answer, label_encoders[i].classes_)
        X[0][i]=label_encoders[i].transform([answer])[0]
        i+=1
    # X=np.asarray(X)
    print(X.shape)
    print(X)
    X=sc.transform(X)
    y=model.predict(X)[0]
    print(y)
    return {"result":float(y) }
    
    
if __name__ == '__main__':
    app.run(host='192.168.22.72')