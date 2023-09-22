from ...database_model import Database

HOST = 'users'
PORT = 5001
DATABASE = 'users_database'
USER = 'user'
PASSWORD = 'password'

USER_DATABASE = Database(HOST, PORT, DATABASE, USER, PASSWORD)
