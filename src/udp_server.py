import data_base as db
import socket
import json
import datetime

class UDPServer:

    data_base = db.DataBase()

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

            try:
                json_data = json.loads(data.decode())
                print(json_data)

                if self.data_base.is_device_registered(json_data['mac']):

                    if json_data['type'] == 'sensor_data':
                        self.new_sensor_data(json_data, addr)

                    if json_data['type'] == 'soil_data':
                        self.new_soil_data(json_data, addr)

                    elif json_data['type'] == 'register_sensor':
                        self.update_device(json_data, addr)

                elif json_data['type'] == 'register_device':
                    self.register_device(json_data, addr)

                else:
                    print("Device not registered")
                    self.sock.sendto("register_device".encode(), addr)

            except json.JSONDecodeError as e:
                print("Error Decoding JSON", e)

    def register_device(self, data, addr):

        self.data_base.insert_device(data['mac'], addr, data['model'], data['location'])

        sensors = data['sensors']
        for sensor in sensors:
            self.data_base.insert_sensors(data['mac'], sensor, sensors[sensor])

        print("Device registered")

    def update_device(self, data, addr):
        self.data_base.update_device(data['mac'], addr, data['model'], data['location'])

        sensors = data['sensors']
        for sensor in sensors:
            self.data_base.insert_sensors(data['mac'], sensor, sensors[sensor])

        print("Device updated")

    def new_sensor_data(self, data, addr):
        time_stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print("Time Stamp:", time_stamp)

        self.data_base.insert_sensor_data(time_stamp, data['mac'], data['temperature'], data['humidity'])
        self.sock.sendto("data recived".encode(), addr)

    def new_soil_data(self, data, addr):
        time_stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print("Time Stamp:", time_stamp)

        self.data_base.insert_soil_data(time_stamp, data['mac'], data['soil_moisture'])
        self.sock.sendto("data recived".encode(), addr)