import data_base as db
import socket
import json
import datetime

database = db.DataBase()

UDP_IP = "0.0.0.0"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print("UDP server is running")

while True:

    data, addr = sock.recvfrom(1024)
    print("received message:", data.decode(), "from", addr)

    try:
        json_data = json.loads(data.decode())
        print(json_data)

        if database.is_device_registered(json_data['mac']):

            print("Device registered")

            time_stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if json_data['type'] == 'sensor_data':
                database.insert_sensor_data(time_stamp, json_data['mac'], json_data['temperature'], json_data['humidity'])
                sock.sendto("data recived".encode(), addr)

            elif json_data['type'] == 'register_sensor':
                database.update_device(json_data['mac'], addr[0], json_data['model'], json_data['location'])

                

        elif json_data['type'] == 'register_device':
            database.insert_device(json_data['mac'], addr[0], json_data['model'], json_data['location'])

            # if 'sensors' in json_data:
            #     for sensor in json_data['sensors']:
            #         database.insert_sensors(json_data['mac'], sensor['name'], sensor['model'])

            print("Device registered")

        else:
            print("Device not registered")
            sock.sendto("register_device".encode(), addr)


    except json.JSONDecodeError as e:
        print("Error Decoding JSON", e)