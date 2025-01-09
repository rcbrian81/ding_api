import mysql.connector
import os
from dotenv import load_dotenv
load_dotenv()

def connect_to_database():
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            charset="utf8mb4",
            collation="utf8mb4_general_ci"  
        )
        print("Successfully connected to the database!")
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

def handle_database_task(data):
    print(f"Handeling db task:\n data:{data}")
    connection = connect_to_database()
    if not connection:
        print("Could not connect to the database.")
        return

    try:
       print("connected to db!")
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    finally:
        connection.close()
        print("Database connection closed.")
