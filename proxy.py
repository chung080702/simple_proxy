import http.server
import socketserver
import urllib.request
import ssl
import logging
from datetime import datetime, timedelta, timezone
import socket
import threading

# Configure logging
logging.basicConfig(
    filename='proxy.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Set timezone to Vietnam (UTC+7)
VN_TZ = timezone(timedelta(hours=7))

PORT = 8080
CERT_FILE = './cert/certfile.pem'
KEY_FILE = './cert/keyfile.pem'

class Proxy(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        logging.info("%s - %s" % (self.client_address[0], format % args))

    def do_GET(self):
        self.handle_request("GET")

    def do_POST(self):
        self.handle_request("POST")

    def do_PUT(self):
        self.handle_request("PUT")

    def do_DELETE(self):
        self.handle_request("DELETE")

    def do_CONNECT(self):
        self.handle_connect()

    def handle_request(self, method):
        self.log_message("Received %s request for %s", method, self.path)
        url = self.path
        try:
            self.log_message("Forwarding %s request to %s", method, url)
            with urllib.request.urlopen(url) as response:
                self.send_response(response.status)
                self.send_header('Content-type', response.headers['Content-type'])
                self.end_headers()
                self.wfile.write(response.read())
            self.log_message("Successfully forwarded %s request to %s", method, url)
        except Exception as e:
            self.log_message("Error forwarding %s request to %s: %s", method, url, e)
            self.send_error(500, f"Error: {e}")

    def handle_connect(self):
        self.log_message("Received CONNECT request for %s", self.path)
        try:
            address = self.path.split(':')
            host = address[0]
            port = int(address[1])
            self.log_message("Connecting to %s:%d", host, port)
            with socket.create_connection((host, port)) as conn:
                self.send_response(200, "Connection Established")
                self.end_headers()
                self.log_message("Connection established for %s", self.path)
                
                # Wrap the connection with SSL if the target is HTTPS
                if port == 443:
                    context = ssl.create_default_context()
                    conn = context.wrap_socket(conn, server_hostname=host)
                
                # Relay data between client and server
                self._relay_data(self.connection, conn)
        except Exception as e:
            self.log_message("Error handling CONNECT request for %s: %s", self.path, e)
            self.send_error(500, f"Error: {e}")

    def _relay_data(self, client_conn, server_conn):
        def forward(source, destination):
            try:
                while True:
                    data = source.recv(4096)
                    if not data:
                        break
                    destination.sendall(data)
            except Exception as e:
                self.log_message("Error relaying data: %s", e)
            finally:
                source.close()
                destination.close()

        client_to_server = threading.Thread(target=forward, args=(client_conn, server_conn))
        server_to_client = threading.Thread(target=forward, args=(server_conn, client_conn))
        client_to_server.start()
        server_to_client.start()
        client_to_server.join()
        server_to_client.join()

# Create an HTTP server and wrap it with SSL
httpd = socketserver.TCPServer(("", PORT), Proxy)
httpd.socket = ssl.wrap_socket(httpd.socket, certfile=CERT_FILE, keyfile=KEY_FILE, server_side=True)

logging.info(f"Serving at port {PORT} with HTTPS")
httpd.serve_forever()