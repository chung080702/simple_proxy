from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/hello', methods=['GET'])
def hello():
    client_port = request.environ.get('REMOTE_PORT')
    print(f"Client is calling from port {client_port}")
    return jsonify(message="Hello, World!")

if __name__ == '__main__':
    port = 5000
    print(f"Server is running on port {port}")
    app.run(host='0.0.0.0', port=port)