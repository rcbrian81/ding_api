from flask import Flask, request
import threading
import database 

app = Flask(__name__)

@app.route('/', methods=['POST'])
def handle_request():
    print("Request received.")
    
    thread = threading.Thread(target=process_request, args=(request.json,))
    thread.start()

    return "New thread create to process requrest!", 202

def process_request(data):
    print("Processing request in new thread")
    print(f"{data}")
    if 'type' in data:
        if data['type'].startswith('database'):
            database.handle_database_task(data)
        else:
            print("Unknown type in request.")
    else:
        print("Invalid request format: 'type' field missing.")

if __name__ == '__main__':
    app.run(port=3672)
