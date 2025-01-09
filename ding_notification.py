import time
from datetime import datetime, timedelta
from database import (
    connect_to_database,
    get_reservations_to_notify,
    get_matches_to_notify,
)


def check_reservations_and_matches():
    print(
        "Notification: Checking Reservations & Matches every minute on seprate thread."
    )
    while True:
        connection = connect_to_database()
        if not connection:
            print("Could not connect to the database. Retrying in 60 seconds...")
            time.sleep(60)
            continue

        try:
            cursor = connection.cursor()

            reservations_to_notify = get_reservations_to_notify(cursor)
            for reservation in reservations_to_notify:
                reservation_id, data = reservation
                print(f"Notifying users for reservation {reservation_id}")

            matches_to_notify = get_matches_to_notify(cursor)
            for match in matches_to_notify:
                match_id, data = match
                print(f"Notifying users for match {match_id}")

        except Exception as e:
            print(f"Error during notification check: {e}")
        finally:
            connection.close()

        time.sleep(60)


if __name__ == "__main__":
    check_reservations_and_matches()
