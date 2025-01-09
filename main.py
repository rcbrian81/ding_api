from flask import Flask, request, jsonify
import threading
import database
from security import validate_security_key
from ding_notification import check_reservations_and_matches

app = Flask(__name__)


@app.route("/", methods=["POST"])
def handle_request():
    print("Request received.")
    provided_key = request.headers.get("Authorization")
    validation_result = validate_security_key(provided_key)

    if validation_result != 1:
        print("Invalid Key: 403")
        # return jsonify({"status": validation_result}), 403

    thread = threading.Thread(target=process_request, args=(request.json,))
    thread.start()

    return "New thread create to process requrest!", 202


def process_request(data):
    print("Processing request in new thread")
    print(f"{data}")
    if "type" in data:
        if data["type"].startswith("database"):
            database.handle_database_task(data)
        else:
            print("Unknown type in request.")
    else:
        print("Invalid request format: 'type' field missing.")


if __name__ == "__main__":
    print("*****Server is running.*****")
    notification_thread = threading.Thread(
        target=check_reservations_and_matches, daemon=True
    )
    notification_thread.start()
    app.run(port=3672)
