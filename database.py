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


def fetch_all(sql, params=()):
    """Fetch all rows from the database for a given query.

    Args:
        sql (str): The SQL query to execute.
        params (tuple, optional): Parameters to pass to the query."""
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params)
        return cur.fetchall()
    finally:
        conn.close()


def fetch_one(sql, params=()):
    """Fetch a single row from the database for a given query.

    Args:
        sql (str): The SQL query to execute.
        params (tuple, optional): Parameters to pass to the query."""
    rows = fetch_all(sql, params)
    return rows[0] if rows else None


def execute(sql, params=()):
    """Execute a query that modifies the database (INSERT, UPDATE, DELETE).

    Args:
        sql (str): The SQL query to execute.
        params (tuple, optional): Parameters to pass to the query."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        conn.commit()
    finally:
        conn.close()
