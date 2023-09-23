import hashlib
from fastapi import HTTPException
from ...database import user_database as db
from ..utils import users_util, sessions_util

def user_login(username: str, password: str):
    hashed_password = hashlib.md5(password.encode()).hexdigest()

    login_result = sessions_util.is_valid_login(username, hashed_password) # returns False if invalid login

    if login_result:
        user_id, role = login_result
        session = sessions_util.create_session(user_id, role)
        return {
            'session_details': session,
            'message': f'User {username} successfully logged in'
        }
    else:
        if users_util.username_exists(username):
            raise HTTPException(status_code=401, detail="Invalid password")
        raise HTTPException(status_code=401, detail="Account does not exist")


def get_all_sessions():
    FIELD_NAMES = ['session_id', 'user_id', 'role', 'creation_time', 'expiration_time']

    rows = db.execute_sql_read_fetchall(f"SELECT * FROM sessions")
    sessions = [dict(zip(FIELD_NAMES, row)) for row in rows]
    return sessions

def get_session(session_id):
    FIELD_NAMES = ['session_id', 'user_id', 'role', 'creation_time', 'expiration_time']

    result = db.execute_sql_read_fetchone('SELECT * FROM sessions WHERE session_id = %s',
                                 params=(session_id,))

    if result and not sessions_util.is_expired_session(result):
        return dict(zip(FIELD_NAMES, result))
    else:
        raise HTTPException(status_code=401, detail="Unauthorized session")

def user_logout(session_id):
    try:
        sessions_util.delete_session(session_id)
        return {
            'message': f'Session {session_id} successfully deleted'
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Unable to logout user: {e}")
