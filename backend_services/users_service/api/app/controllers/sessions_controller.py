import hashlib
from api_models.error import ServiceError
from api_models.users import GetSessionResponse, UserLoginResponse, UserLogoutResponse
from user_database import USER_DATABASE as db
from utils import users_util, sessions_util

def user_login(username: str, password: str) -> UserLoginResponse | ServiceError:
    hashed_password = hashlib.md5(password.encode()).hexdigest()

    login_result = sessions_util.is_valid_login(username, hashed_password) # returns False if invalid login

    if login_result:
        user_id, role = login_result
        session_id = sessions_util.create_session(user_id, role)
        return UserLoginResponse(session_id=session_id, message=f'User {username} successfully logged in with {session_id}')
    else:
        if users_util.username_exists(username):
            return ServiceError(status_code=401, message='Invalid password')
        return ServiceError(status_code=401, message='Account does not exist')

def get_all_sessions() -> list[GetSessionResponse]:
    FIELD_NAMES = ['session_id', 'user_id', 'role', 'creation_time', 'expiration_time']

    rows = db.execute_sql_read_fetchall(f"SELECT * FROM sessions")
    sessions = [dict(zip(FIELD_NAMES, row)) for row in rows]
    return [GetSessionResponse(**x) for x in sessions]

def get_session(session_id: str) -> GetSessionResponse | ServiceError:
    FIELD_NAMES = ['session_id', 'user_id', 'role', 'creation_time', 'expiration_time']

    result = db.execute_sql_read_fetchone('SELECT * FROM sessions WHERE session_id = %s',
                                 params=(session_id,))

    if result is None:
        return ServiceError(status_code=401, message='Unauthorized session')

    expiration_time: str = result[4]
    if sessions_util.is_expired_session(expiration_time):
        return GetSessionResponse(**dict(zip(FIELD_NAMES, result)))

    return ServiceError(status_code=401, message='Unauthorized session')

def user_logout(session_id: str) -> UserLogoutResponse | ServiceError:
    try:
        sessions_util.delete_session(session_id)
        return UserLogoutResponse(message=f'Session {session_id} successfully deleted')
    except Exception as e:
        return ServiceError(status_code=500, message=f'Unable to logout user: {e}')

