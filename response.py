import requests
import json

url = 'http://127.0.0.1:5000/login'  # Update the URL if necessary
data = {
    "email": "pourneemakulkarni@gmail.com",
    "password": "123456"
}

response = requests.post(url, json=data)

print(response.status_code)
print(response.json())
