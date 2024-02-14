from udp_server import client_handler
from json_to_db import DataBase
import matplotlib.pyplot as plt
from datetime import datetime

def server():
	udp_server = client_handler()
	udp_server.run()
 
def main():
    db = DataBase()
    data = db.get_data('8C:AA:B5:15:F8:E8', 'room monitor', 'temperature')

    x = [datetime.strptime(x[1], '%Y-%m-%d %H:%M:%S').strftime('%H:%M:%S') for x in data]
    y = [x[0] for x in data]
    print(x)
    plt.plot(y)
    plt.show()
	
	

if __name__ == "__main__":
	main()