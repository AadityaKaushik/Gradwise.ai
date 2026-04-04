import os
import psycopg2
from psycopg2 import pool
from dotenv import load_dotenv

load_dotenv()

_connection_pool = pool.ThreadedConnectionPool(
    minconn=2,
    maxconn=20,
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    port=os.getenv("DB_PORT")
)

def get_connection():
    return _connection_pool.getconn()

def return_connection(conn):
    _connection_pool.putconn(conn)
