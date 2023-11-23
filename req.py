import requests
import json
import numpy as np

# Your new data sample
new_data_sample = np.array([
    '45 or older', 'Others', 'Neutral', 'Yes, many', 'Other', 'Neutral', 'Nearly every day', 'Rarely',
    'Not at all', 'Very Good', 'Never', 'Within the past week', "I can't remember", 'Nearly every day', 'Every night',
    'No', 'Yes, one medication/treatment', 'Good', 'Yes, very frequently', 'Never', 'A little',
    'Yes, in the past 6 months', 'More than 10 hours', 'Good', 'In a relationship', 'Very discontent', 'Never',
    'Occasionally', "No, I haven't changed my job recently", 'No'
])

# Convert the numpy array to a list for serialization
data_to_send = new_data_sample.tolist()

# API endpoint URL
url = 'http://192.168.1.6:5000/predict'

# Send the POST request with the data
try:
    response = requests.post(url, json=data_to_send)
    if response.status_code == 200:
        # Successful request
        result = response.json()
        print("Prediction Result:", result)
    else:
        # Handle unsuccessful request
        print("Request failed with status code:", response.status_code)
        print("Error message:", response.text)
except requests.RequestException as e:
    # Handle exceptions if the request fails
    print("Request failed:", e)








# @app.route('/predict', methods=['POST'])
# def predict():
#     # label_encoders = []
#     # for col in range(X.shape[1]):
#     #     if isinstance(X[0, col], str):
#     #         label_encoder = LabelEncoder()
#     #         X[:, col] = label_encoder.fit_transform(X[:, col])
#     #         label_encoders.append(label_encoder)

    
#     try:
#         data = request.get_json()
        
#         # Perform preprocessing steps to match the model's requirements
#         processed_data = np.array([data])  # Assuming 'data' is a single sample
#         for col, label_encoder in enumerate(label_encoders):
#             if isinstance(processed_data[0, col], str):
#                 processed_data[0, col] = label_encoder.transform([processed_data[0, col]])
        
#         processed_data = sc.transform(processed_data)
        
#         # Perform prediction
#         predictions = model.predict(processed_data)
#         result = {'prediction': predictions.tolist()}  # Convert predictions to a list
        
#         return jsonify(result), 200
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500
    