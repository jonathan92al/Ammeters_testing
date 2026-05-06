from socket import socket, AF_INET, SOCK_STREAM


def request_current_from_ammeter(port: int, command: bytes):
    with socket(AF_INET, SOCK_STREAM) as s:
        s.connect(('localhost', port))
        s.sendall(command)
        data = s.recv(1024)
        if data:
            decoded_data = data.decode('utf-8')
            print(f"Received current measurement from port {port}: {decoded_data} A")
            return float(decoded_data)
        else:
            print("No data received.")
            return None
