import udp_server


def main():
    server = udp_server.UDPServer()

    server.run()

if __name__ == "__main__":
    main()