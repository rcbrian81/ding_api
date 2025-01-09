from database import (
    connect_to_database,
    update_match_for_user_1,
    create_reservation,
    remove_reservation,
    remove_match,
)


def reject_match(match_id):
    connection = connect_to_database()
    if not connection:
        return "0_db_connection"

    try:
        cursor = connection.cursor()
        result = remove_match(cursor, match_id)
        connection.commit()
        return result
    except Exception as e:
        print(f"Error in reject_match: {e}")
        return "0_con_0001"
    finally:
        connection.close()
