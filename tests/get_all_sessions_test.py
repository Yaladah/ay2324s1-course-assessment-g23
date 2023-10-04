import requests

session_id = "all"
response_get_all_sessions = requests.get("http://localhost:8000/sessions_all")
print("Get all sessions:")
print(response_get_all_sessions.content)