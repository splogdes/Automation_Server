from udp_server import client_handler
from json_to_db import DataBase
import matplotlib.pyplot as plt
from datetime import datetime

def server():
	udp_server = client_handler()
	udp_server.run()
 
def main():
    db = DataBase()
    data1 = db.get_data('5C:CF:7F:02:59:0E', 'room monitor', 'temperature')
    data2 = db.get_data('5C:CF:7F:02:59:0E', 'room monitor', 'humidity')
    # data = db.get_data('5C:CF:7F:02:59:0E', 'gas sensor', 'air_quality')
    # print(data)
    x1 = [datetime.strptime(x[1], '%Y-%m-%d %H:%M:%S') for x in data1]
    y1 = [x[0] for x in data1]
    x2 = [datetime.strptime(x[1], '%Y-%m-%d %H:%M:%S') for x in data2]
    y2 = [x[0] for x in data2]
    fig , ax = plt.subplots(2,1)
    ax[0].plot(x1, y1)
    ax[1].plot(x2, y2)
    ax[0].set_title('Temperature')
    ax[1].set_title('Humidity')
    plt.show()
	
	

if __name__ == "__main__":
    main()
	# server()