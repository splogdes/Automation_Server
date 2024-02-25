from udp_server import client_handler
from json_to_db import DataBase
import matplotlib.pyplot as plt
from datetime import datetime

def server():
	udp_server = client_handler()
	udp_server.run()
 
def main():
    db = DataBase()
    data = db.get_data('5C:CF:7F:02:59:0E', 'room monitor', 'temperature')
    print(data)
    x = [datetime.strptime(x[1], '%Y-%m-%d %H:%M:%S') for x in data]
    y = [x[0] for x in data]
    plt.plot(x, y)
    plt.show()
	
	

if __name__ == "__main__":
    main()
	# server()