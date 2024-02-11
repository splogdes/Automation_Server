import socket

class UDPServer:
    def __init__(self, ip = '0.0.0.0', port = 5005):
        self.ip = ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.ip, self.port))

    def run(self):
        print("UDP server is running")

        while True:
            data, addr = self.sock.recvfrom(1024)
            print("received message:", data.decode(), "from", addr)



            message = "Hello, I am UDP server"
            self.sock.sendto(message.encode(), addr)