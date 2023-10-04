import time
import unittest
import requests
import websockets
import asyncio

class TestCodes(unittest.TestCase):
    def test_user_login(self):
        username = "admin"
        password = "password"
        request_data = {
            "username": username,
            "password": password
        }
        response_login = requests.post("http://localhost:8000/sessions", json=request_data)
        print("User login:")
        print(response_login.content)
        print("")
        self.assertEqual(response_login.status_code, 200)

    def test_get_all_users(self):
        user_id = "all"
        # user_id="121d480c-de96-4f72-abca-0a31586ccb28"
        response_get_all_users = requests.get(f"http://localhost:8000/users_all")
        print("Get all users:")
        print(response_get_all_users.content)
        print("")
        self.assertEqual(response_get_all_users.status_code, 200)

    def test_get_all_sessions(self):
        session_id = "all"
        response_get_all_sessions = requests.get("http://localhost:8000/sessions", json=session_id)
        print("Get all sessions:")
        print(response_get_all_sessions.content)
        print("")
        self.assertEqual(response_get_all_sessions.status_code, 200)

    def test_create_user(self):
        data = {
                    "username": "testuser2",
                    "email": "test2@example.com",
                    "password": "testpassword"
                }
        response = requests.post("http://localhost:8000/users", json=data)
        print("Create new user")
        print(response.content)
        print("")
        self.assertEqual(response.status_code, 200)
        
    def test_create_question(self):
        data = {
            "title": "test",
            "description": "testDesc",
            "category": "python",
            "complexity": "Easy"
        }
        response = requests.post("http://localhost:8000/questions", json=data)
        print("Create new question")
        print(response.content)
        
    def test_get_all_questions(self):
        response = requests.get("http://localhost:8000/questions_all")
        print("Get all questions")
        print(response.content)
        print("")
        self.assertEqual(response.status_code, 200)
        
    async def setUp(self):
        self.websocket = await websockets.connect('ws://localhost:8000/ws')

    async def tearDown(self):
        await self.websocket.close()

    async def test_send_message(self):
        self.websocket = await websockets.connect('ws://localhost:8000/ws')
        message = {
            'service': 'matching-service',
            'message': {
                'user_id': '123',
                'complexity': 'easy'
            }
        }
        await self.websocket.send(message.json())
        response = await self.websocket.recv()
        print(response)
        await self.websocket.close()
        self.assertEqual(response, "Received: Hello, WebSocket!")


# if __name__ == "__main__":
#     unittest.main()