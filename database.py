import mariadb
import os
from dotenv import load_dotenv
from datetime import datetime
from cryptography.fernet import Fernet
import json

load_dotenv()


def connect_to_database():
    try:
        connection = mariadb.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            autocommit=True,
        )
        print("Successfully connected to the database!")
        return connection
    except mariadb.Error as err:
        print(f"Error: {err}")
        return None


def handle_database_task(data):
    types = ["database_acc_register", "database_acc_login"]
    print(f"Handling db task:\n data: {data}")
    connection = None
    if data["type"] in types:
        connection = connect_to_database()
    if not connection:
        print("Could not connect to the database.")
        return 0

    try:
        print("Connected to db!")
        if data["type"] == "database_acc_register":
            result = database_acc_register(data, connection)
            print(f"Registration result: {result}")
        elif data["type"] == "database_acc_login":
            result = database_acc_login(data, connection)
            print(f"Login result: {result}")
    except mariadb.Error as err:
        print(f"Database error: {err}")
    finally:
        if connection:
            connection.close()
            print("Database connection closed.")


def database_acc_register(data, connection):
    print("Registering account")

    username = data["username"]
    if not (username.isalnum() or "_" in username or "-" in username):
        return "0_con_0001"
    password = data["password"]
    if not all(char.isalnum() or char in "!@#$%^&*" for char in password):
        return "0_con_0002"

    # Encrypt the password
    # encrypted_password = fernet.encrypt(password.encode()).decode()
    encrypted_password = "hash"
    account_data = {
        "username": username,
        "password": encrypted_password,
        "date_created": datetime.now().isoformat(),
        "first_name": data.get("first_name", ""),
        "last_name": data.get("last_name", ""),
        "dob": data.get("dob", ""),
        "email": data.get("email", ""),
        "school": data.get("school", ""),
        "demo": data.get("demo", ""),
        "groups": {},
    }

    try:
        cursor = connection.cursor()
        query = "INSERT INTO accounts (email, data) VALUES (?,?)"
        cursor.execute(
            query,
            (
                data["email"],
                json.dumps(account_data),
            ),
        )
        connection.commit()
        return "1"
    except mariadb.Error as e:
        print(f"Database error: {e}")
        return f"0_db_{str(e.errno)}"
    finally:
        cursor.close()


def database_acc_login(data, connection):
    print("Logging in account")
    identifier = data["identifier"]
    password = data["password"]

    try:
        cursor = connection.cursor()

        query = """
        SELECT JSON_EXTRACT(data, '$.password')
        FROM accounts
        WHERE email = ? OR JSON_EXTRACT(data, '$.username') = ?
        """
        cursor.execute(query, (identifier, identifier))
        result = cursor.fetchone()

        if result:
            print(f"this is the result: {result}")
            stored_password = result[0].strip('"')
            if stored_password == password:
                return "1"
            else:
                return "0_db_0002"
        else:
            return "0_db_0003"
    except mariadb.Error as e:
        print(f"Database error: {e}")
        return f"0_db_{str(e.errno)}"
    finally:
        cursor.close()
