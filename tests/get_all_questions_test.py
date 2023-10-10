import requests

response = requests.get("http://localhost:8000/questions_all")
print("Get all questions")
print(response.content)