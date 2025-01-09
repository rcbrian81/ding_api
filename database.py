import mariadb
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

import json
import bcrypt

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

    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    account_data = {
        "username": username,
        "password": hashed_password,
        "date_created": datetime.now().isoformat(),
        "first_name": data.get("first_name", ""),
        "last_name": data.get("last_name", ""),
        "dob": data.get("dob", ""),
        "email": data.get("email", ""),
        "school": data.get("school", ""),
        "demo": data.get("demo", ""),
        "groups": {"company_ding": {"position": "", "matches": [], "reservations": []}},
        "notifications": "",
        "rating": "",
        "ratings_total": "",
        "rating_waiting": "",
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
            if bcrypt.checkpw(password.encode(), stored_password.encode()):
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


def insert_match(id, user_1, user_2, opened, accounts, users_accepted, connection):
    try:
        data = json.dumps(
            {
                "id": id,
                "opened": opened,
                "accounts": accounts,
                "users_accepted": users_accepted,
            }
        )

        query = """
        INSERT INTO matches (id, user_1, user_2, data, created_at)
        VALUES (?, ?, ?, ?, NOW())
        """

        cursor = connection.cursor()
        cursor.execute(query, (id, user_1, user_2, data))
        connection.commit()
        return 1  # Success
    except mariadb.Error as e:
        return f"0_db_{e.errno}"
    except Exception as e:
        return "0_con_1001"


def insert_reservation(
    id, user_1, user_2, opened, accounts, users_accepted, connection
):
    try:
        data = json.dumps(
            {
                "id": id,
                "opened": opened,
                "accounts": accounts,
                "users_accepted": users_accepted,
            }
        )

        query = """
        INSERT INTO reservations (id, user_1, user_2, data, created_at)
        VALUES (?, ?, ?, ?, NOW())
        """

        cursor = connection.cursor()
        cursor.execute(query, (id, user_1, user_2, data))
        connection.commit()
        return 1  # Success
    except mariadb.Error as e:
        return f"0_db_{e.errno}"
    except Exception as e:
        return "0_con_1001"


def insert_post(
    id,
    user_1,
    account,
    date,
    title,
    body,
    location_pickup,
    location_pickup_coords,
    location_dropoff,
    location_dropoff_coords,
    connection,
):
    try:
        data = json.dumps(
            {
                "id": id,
                "account": account,
                "date": date,
                "title": title,
                "body": body,
                "location_pickup": location_pickup,
                "location_pickup_coords": location_pickup_coords,
                "location_dropoff": location_dropoff,
                "location_dropoff_coords": location_dropoff_coords,
            }
        )

        query = """
        INSERT INTO posts (id, user_1, data, created_at)
        VALUES (?, ?, ?, NOW())
        """

        cursor = connection.cursor()
        cursor.execute(query, (id, user_1, data))
        connection.commit()
        return 1  # Success
    except mariadb.Error as e:
        return f"0_db_{e.errno}"  # Database error
    except Exception as e:
        return "0_con_1001"  # Generic error for other exceptions


def remove_match(cursor, match_id):
    try:
        cursor.execute("DELETE FROM matches WHERE id = %s", (match_id,))
        if cursor.rowcount == 0:
            return "0_db_404"  # Match ID not found
        return 1
    except mariadb.Error as e:
        return f"0_db_{e.errno}"


def update_match_for_user_1(cursor, match_id):

    try:
        query = "UPDATE matches SET data = JSON_SET(data, '$.users_accepted[0]', TRUE) WHERE id = %s"
        cursor.execute(query, (match_id,))
        if cursor.rowcount == 0:
            return "0_db_404"
        return 1
    except mariadb.Error as e:
        return f"0_db_{e.errno}"


def create_reservation(cursor, user_1, user_2, reservation_id, match_data):

    try:
        reservation_data = {
            "id": reservation_id,
            "opened": "true",
            "accounts": [user_1, user_2],
            "users_accepted": [user_1, user_2],
        }
        cursor.execute(
            "INSERT INTO reservations (user_1, user_2, data, created_at) VALUES (%s, %s, %s, NOW())",
            (user_1, user_2, json.dumps(reservation_data)),
        )
        return 1
    except mariadb.Error as e:
        return f"0_db_{e.errno}"


def remove_reservation(cursor, reservation_id):

    try:
        cursor.execute("DELETE FROM reservations WHERE id = %s", (reservation_id,))
        if cursor.rowcount == 0:
            return "0_db_404"
        return 1
    except mariadb.Error as e:
        return f"0_db_{e.errno}"


def get_reservations_to_notify(cursor):

    try:
        now = datetime.now()
        one_day_later = (now + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
        today = now.strftime("%Y-%m-%d %H:%M:%S")

        query = """
            SELECT id, data
            FROM reservations
            WHERE JSON_EXTRACT(data, '$.opened') = 'true'
            AND JSON_EXTRACT(data, '$.date') <= ?
            AND JSON_EXTRACT(data, '$.date') > ?
        """
        cursor.execute(query, (one_day_later, today))
        return cursor.fetchall()
    except mariadb.Error as e:
        print(f"Error fetching reservations: {e}")
        return []


def get_matches_to_notify(cursor):

    try:
        now = datetime.now()
        three_days_later = (now + timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S")
        today = now.strftime("%Y-%m-%d %H:%M:%S")

        query = """
            SELECT id, data
            FROM matches
            WHERE JSON_LENGTH(JSON_EXTRACT(data, '$.users_accepted')) = 1
            AND JSON_EXTRACT(data, '$.date') <= ?
            AND JSON_EXTRACT(data, '$.date') > ?
        """
        cursor.execute(query, (three_days_later, today))
        return cursor.fetchall()
    except mariadb.Error as e:
        print(f"Error fetching matches: {e}")
        return []
