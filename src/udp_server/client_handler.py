from json_to_db import jdb
import socket
import json

class client_handler:    

	def __init__(self, ip = '0.0.0.0', port = 5005):
		self.ip = ip
		self.port = port
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.data_base = jdb(self.sock)
		self.sock.bind((self.ip, self.port))

	def run(self):
		print("UDP server is running")

		while True:
			data, addr = self.sock.recvfrom(1024)
			print("received message:", data.decode(), "from", addr)

			try:
				json_data = json.loads(data.decode())
				self.process_request(json_data, addr)
					
			except json.JSONDecodeError as e:
				print("Error Decoding JSON", e)

		
	def process_request(self, data, addr):

		if not self.data_base.is_device_registered(data):
			if data['message_type'] == 'register_device':
				self.data_base.register_device(data, addr)
			else:
				self.sock.sendto('register_device'.encode(), addr)
				return
			
		match data['message_type']:

			case 'register_sensor':
				self.data_base.register_sensor(data, addr)

			case 'sensor_data':
				self.data_base.new_sensor_data(data, addr)

			case 'register_device':
				self.data_base.update_device(data, addr)

			case _:
				print("Message Not Recougnised")
				self.sock.sendto('Message Not Recougnised'.encode(), addr)