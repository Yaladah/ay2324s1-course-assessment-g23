import unittest
import requests

username = "admin"
password = "password"

request_data = {
    "username": username,
    "password": password
}
response = requests.post("http://localhost:8000/sessions", json=request_data)


print(response.content)