from ...database_model import Database

HOST = 'questions'
PORT = 5002
DATABASE = 'questions_database'
USER = 'user'
PASSWORD = 'password'

USER_DATABASE = Database(HOST, PORT, DATABASE, USER, PASSWORD)
