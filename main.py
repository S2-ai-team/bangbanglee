import socket
import json

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

HOST = config["RASPBERRY_IP"]
PORT = config["PORT"]
api_key = config["API_KEY"]

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

try:
    while True:
        msg = input("보낼 메시지: ").strip()
        full_message = api_key + "\n" + msg
        client_socket.sendall(full_message.encode())
except KeyboardInterrupt:
    pass
finally:
    client_socket.close()
