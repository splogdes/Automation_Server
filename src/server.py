from udp_server import client_handler

if __name__ == '__main__':
    server = client_handler('192.168.1.178')
    server.run()