#!/usr/bin/python3
from seed import connect_to_prodev

def stream_users():
    """Generator function that streams rows from user_data table"""
    connection = connect_to_prodev()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user_data")
        
        for row in cursor:
            yield row
            
        cursor.close()
        connection.close()