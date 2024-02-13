from udp_server import client_handler

def main():
    
    server = client_handler()

    server.run()

if __name__ == "__main__":
    main()