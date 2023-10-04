import unittest
import requests

data = {
            "username": "testuser2",
            "email": "test2@example.com",
            "password": "testpassword"
        }

response = requests.post("http://localhost:8000/users", json=data)
print(response.content)

