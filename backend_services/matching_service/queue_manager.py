from .matching_util import User

queue = []

def check_for_matches():
    global queue
    while True:
        if len(queue) >= 2:
            user1 = queue.pop(0)
            user2 = queue.pop(0)
            notify_users_of_match(user1, user2)

def notify_users_of_match(user1: User, user2: User):
    user1.websocket.send_text(f"You have matched with {user2.user_id}")
    user2.websocket.send_text(f"You have matched with {user1.user_id}")
