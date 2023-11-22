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
