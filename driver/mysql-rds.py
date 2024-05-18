import mysql.connector
from mysql.connector import Error


def get_instance():
    config = {
        "host": "database-1.cpigwcyuk6vv.us-east-2.rds.amazonaws.com",
        "user": "admin",
        "password": "SO9yvDX5GwQfF1EWEM5u",
        "database": "economizei",
    }

    try:
        db = mysql.connector.connect(**config)
        if db.is_connected():
            cursor = db.cursor()
            print("Successfully connected to the database")
            return cursor
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None
