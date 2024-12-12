#!/usr/bin/python3
import sqlite3
import functools
from datetime import datetime

def log_queries(func):
    """Decorator to log SQL queries"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Log the query if it's passed as an argument
        query = kwargs.get('query') or args[0] if args else None
        if query:
            timestamp = datetime.now()
            print(f"[{timestamp}] {query}")
        return func(*args, **kwargs)
    return wrapper

@log_queries
def fetch_all_users(query):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

#### fetch users while logging the query
users = fetch_all_users(query="SELECT * FROM users")