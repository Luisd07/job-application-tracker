"""Database connection helper."""
import os

import mysql.connector
from dotenv import load_dotenv

# Read the variables from the .env file into the environment.
load_dotenv()


def get_connection():
    """Open and return a new MySQL connection.

    The caller is responsible for closing it (conn.close()).
    Connection settings come from environment variables (see .env.example).
    """
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
    )
