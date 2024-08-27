import requests
import socket


# Disable warnings about insecure connections
# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Create a temporary socket to determine the client's port
temp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
temp_socket.bind(('', 0))  # Bind to an available port
client_port = temp_socket.getsockname()[1]
temp_socket.close()

print(f"Client is using port {client_port} to send the request")

url = 'https://price.mazig.io/price/orai'
# url = 'http://localhost:5000/hello'
proxies = {
    'http': 'https://localhost:8080', 
    'https': 'https://localhost:8080',  
}

response = requests.get(url, proxies=proxies, verify=False)

if response.status_code == 200:
    print(response.json())
else:
    print(f"Failed to get response: {response.status_code}")