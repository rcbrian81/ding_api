from database import (
    connect_to_database,
    update_match_for_user_1,
    create_reservation,
    remove_reservation,
    remove_match,
)


def accept_match_user_1(match_id, user_2_email):

    connection = connect_to_database()
    if not connection:
        return "0_db_connection"

    try:
        cursor = connection.cursor()
        result = update_match_for_user_1(cursor, match_id)
        if result == 1:

            send_email(user_2_email, "DING Match", "User 1 has accepted your match!")
        return result
    finally:
        connection.close()


def accept_match_user_2(match_id, user_1_email, user_2_email):

    connection = connect_to_database()
    if not connection:
        return "0_db_connection"

    try:
        cursor = connection.cursor()

        cursor.execute(
            "SELECT user_1, user_2, data FROM matches WHERE id = %s", (match_id,)
        )
        match = cursor.fetchone()
        if not match:
            return "0_db_404"

        user_1, user_2, match_data = match
        reservation_id = f"res_{match_id}"
        result = create_reservation(cursor, user_1, user_2, reservation_id, match_data)
        if result == 1:

            cursor.execute("DELETE FROM matches WHERE id = %s", (match_id,))

            send_email(
                user_1_email,
                "DING Reservation",
                "User 2 has accepted your reservation!",
            )
            send_email(
                user_2_email, "DING Reservation", "You have accepted the reservation!"
            )
        return result
    finally:
        connection.close()


def cancel_reservation(reservation_id, user_1_email, user_2_email, reason):

    connection = connect_to_database()
    if not connection:
        return "0_db_connection"

    try:
        cursor = connection.cursor()
        result = remove_reservation(cursor, reservation_id)
        if result == 1:
            send_email(
                user_1_email,
                "DING Reservation",
                f"User 2 has canceled the reservation. Reason: {reason}",
            )
            send_email(
                user_2_email,
                "DING Reservation",
                f"You have canceled the reservation. Reason: {reason}",
            )
        return result
    finally:
        connection.close()


def send_email(email, subject, body):

    print(f"Sending email to {email} with subject '{subject}' and body:\n{body}")
