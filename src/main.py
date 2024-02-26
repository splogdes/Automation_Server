from udp_server import client_handler
from json_to_db import DataBase
import matplotlib.pyplot as plt
from datetime import datetime
import sys

def server():
	udp_server = client_handler()
	udp_server.run()
 
def get_data(sname, type, db):
    data = db.get_data('5C:CF:7F:02:59:0E', sname, type, 4)
    x = [datetime.strptime(x[1], '%Y-%m-%d %H:%M:%S') for x in data]
    y = [x[0] for x in data]
    return x,y

def update(lines, axs, db):
    room_monitor = ['temperature', 'humidity']
    gas_sensor = ['eco2', 'tvoc', 'air_quality']
    
    for i in range(len(room_monitor)):
        x , y = get_data('room monitor',room_monitor[i], db)
        lines[0][i].set_xdata(x)
        lines[0][i].set_ydata(y)
        axs[0][i].relim()
        axs[0][i].autoscale_view()
        
    for i in range(len(gas_sensor)):
        x , y = get_data('gas sensor',gas_sensor[i], db)
        lines[1][i].set_xdata(x)
        lines[1][i].set_ydata(y)
        axs[1][i].relim()
        axs[1][i].autoscale_view()
        
def set_up(db):

    room_monitor = ['temperature', 'humidity']
    gas_sensor = ['eco2', 'tvoc', 'air_quality']
    
    lines1 = []
    fig1, ax1 = plt.subplots(2)
    
    for i in range(len(room_monitor)):
        x , y = get_data('room monitor',room_monitor[i], db)
        line, = ax1[i].plot(x,y)
        ax1[i].set_title(room_monitor[i])
        lines1.append(line)
        
    fig2, ax2 = plt.subplots(3)
    lines2 = []
    
    for i in range(len(gas_sensor)):
        x , y = get_data('gas sensor',gas_sensor[i], db)
        line, = ax2[i].plot(x,y)
        ax2[i].set_title(gas_sensor[i])
        lines2.append(line)
        
    return [ax1, ax2] , [lines1, lines2]
        

def main():
    db = DataBase()
    plt.ion()
    axs, lines = set_up(db)
    while True:
        update(lines, axs, db)
        plt.draw()
        plt.pause(5)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        server()
    else:
        main()
