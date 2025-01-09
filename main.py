from flask import Flask, request
import threading

app = Flask(__name__)

@app.route('/', methods=['POST'])
def handle_request():
    print("Request received.")
    
    thread = threading.Thread(target=process_request, args=(request.json,))
    thread.start()

    return "New thread create to process requrest!", 202

def process_request(data):
    print(f"Processing request in new thread")

if __name__ == '__main__':
    app.run(port=3672)
