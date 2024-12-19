from . import data_base as db
import socket

class json_to_db:
    '''This class is used to process the data received from the UDP server and insert it into the database'''

    def __init__(self, sock: socket.socket, db_name = 'data.db'):
        '''Initializes the class with the socket and the database name'''
        self.sock = sock
        self.__data_base = db.DataBase(db_name)


    def is_device_registered(self, data):
        '''Checks if the device is already registered in the database'''
        return self.__data_base.is_device_registered(data['mac'])
    
    def register_device(self, data, addr):
        '''Registers the device in the database'''
        self.__data_base.insert_device(data['mac'], addr[0], addr[1], data['model'], data['location'])
        print("Device registered")

    def register_sensor(self, data, addr):
        '''Registers the sensor in the database'''
        if not self.__data_base.is_sensor_registered(data['mac'], data['name']):
            self.__data_base.insert_sensor(data['mac'], data['name'], data['model'])
            for mode in data['modes']:
                self.__data_base.insert_sensor_modes(data['model'], mode, data['modes'][mode])
            self.sock.sendto(("registerd sensor:" + data['name']).encode(), addr)

    def update_device(self, data, addr):
        '''Updates the device in the database'''
        self.__data_base.update_device(data['mac'], addr[0], addr[1], data['model'], data['location'])
        self.sock.sendto("device updated".encode(), addr)

    def new_sensor_data(self, data, addr):
        '''Inserts the sensor data into the database'''
        
        for sensor in data['sensors']:
            if not self.__data_base.is_sensor_registered(data['mac'], sensor):
                self.sock.sendto(sensor.encode(), addr)

        self.__data_base.insert_message(data['mac'], data['sensors'])
        for sensor in data['sensors']:
            self.sock.sendto(("sensor data received " + sensor).encode(), addr)

    def check_integrity(self, data):
        '''Checks the integrity of the data'''
        keys = ['mac', 'message_type']
        return all(key in data for key in keys)