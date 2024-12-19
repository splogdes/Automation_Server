import sqlite3
class DataBase:
	'''This class is used to interact with the database'''

	def __init__(self, db_name = 'data.db'):
		self.conn = sqlite3.connect(db_name)
		self.cursor = self.conn.cursor()
		self.create_table()

	def create_table(self):
		'''Creates the tables if they do not exist'''

		self.cursor.execute('''
					CREATE TABLE IF NOT EXISTS
					DEVICES(
						mac_address VARCHAR(17) PRIMARY KEY,
						ip_address VARCHAR(15) NOT NULL,
						port INTEGER(5) NOT NULL,
						model VARCHAR(50),
						location VARCHAR(50)
					)''')

		self.conn.execute('''
					CREATE TABLE IF NOT EXISTS
					SENSORS(
						sname VARCHAR(50),
						mac_address VARCHAR(17),
						model VARCHAR(50),
						PRIMARY KEY(mac_address, sname),
						FOREIGN KEY(mac_address) REFERENCES DEVICES(mac_address)
                        FOREIGN KEY(model) REFERENCES SMODES(model)
					)''')


		self.conn.execute('''
					CREATE TABLE IF NOT EXISTS
					MESSAGES(
						message_id INTEGER PRIMARY KEY AUTOINCREMENT,
						mac_address VARCHAR(17),
						timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
						FOREIGN KEY(mac_address) REFERENCES DEVICES(mac_address)
					)''')

		self.conn.execute(''' CREATE TABLE IF NOT EXISTS
					DATA(
						did INTEGER PRIMARY KEY AUTOINCREMENT,
						message_id INTEGER,
						sname INTEGER,
						value DOUBLE,
						type VARCHAR(50),
						FOREIGN KEY(message_id) REFERENCES MESSAGES(message_id),
						FOREIGN KEY(sname) REFERENCES SENSORS(sname)
					)''')

		self.conn.execute(''' CREATE TABLE IF NOT EXISTS
					SMODES(
						model VARCHAR(50),
						mode VARCHAR(50),
						PRIMARY KEY(model, mode),
						FOREIGN KEY(model) REFERENCES SENSORS(model)
					)''')

		self.conn.commit()

	def insert_sensor_modes(self, model, modes):
		'''Inserts the sensor modes into the database if they do not exist'''
		if not self.cursor.execute('''SELECT * FROM SMODES WHERE model = ?''', (model,)).fetchone():
			for mode in modes:
				self.cursor.execute('''INSERT INTO SMODES(model, mode) VALUES(?,?)''', (model, mode))
				self.conn.commit()

	def insert_device(self, mac_address, ip_address, port, model, location):
		self.cursor.execute(
			'''INSERT INTO DEVICES(mac_address, ip_address, port, model, location) VALUES(?,?,?,?,?)''',
			(mac_address, ip_address, port, model, location)
			)
		self.conn.commit()

	def insert_sensor(self, mac_address, sensor_name, model):
		self.cursor.execute(
			'''INSERT INTO SENSORS(mac_address, sname, model) VALUES(?,?,?)''',
			(mac_address, sensor_name, model)
			)
		self.conn.commit()

	def insert_message(self, mac_address, data = None):
		if data is None:
			data = {}
		self.cursor.execute('''INSERT INTO MESSAGES(mac_address) VALUES(?)''', (mac_address,))
		message_id = self.cursor.lastrowid
		for sensor_name, sensors in data.items():
			for mode , value in sensors.items():
				self.cursor.execute(
					'''INSERT INTO DATA(message_id, sname, value, type) VALUES(?,?,?,?)''',
					(message_id, sensor_name, value, mode)
					)
		self.conn.commit()

	def is_device_registered(self, mac_address):
		self.cursor.execute('''SELECT * FROM DEVICES WHERE mac_address = ?''', (mac_address,))
		return self.cursor.fetchone() is not None

	def is_sensor_registered(self, mac_address, sname):
		self.cursor.execute('''
							SELECT * FROM SENSORS WHERE mac_address = ? AND sname = ?''',
							(mac_address, sname)
							)
		return self.cursor.fetchone() is not None

	def update_device(self, mac_address, ip_address, port, model, location):
		self.cursor.execute('''
							UPDATE DEVICES SET ip_address = ?, port = ?, model = ?, location = ? WHERE mac_address = ?''',
							(ip_address, port, model, location, mac_address)
							)
		self.conn.commit()
  
	def get_devices(self):
		self.cursor.execute('''SELECT mac_address FROM DEVICES''')
		return self.cursor.fetchall()

	def get_sensors(self, mac_address):
		self.cursor.execute('''SELECT sname FROM SENSORS WHERE mac_address = ?''', (mac_address,))
		return self.cursor.fetchall()

	def get_sensor_modes(self, sname):
		self.cursor.execute('''SELECT DISTINCT type FROM DATA WHERE sname = ?''', (sname,))
		return self.cursor.fetchall()
		# self.cursor.execute('''SELECT mode FROM SMODES WHERE model = ?''', (sname,))
		# return self.cursor.fetchall()
  
	def get_data(self, mac_address, sname, mode, duration = 4):
		self.cursor.execute(f'''
							SELECT value, timestamp
                            FROM DATA NATURAL JOIN MESSAGES
       						WHERE mac_address = ? AND sname = ? AND type = ? AND timestamp > datetime('now', '-{duration} hours')
                            ORDER BY timestamp''',
                            (mac_address, sname, mode)
							)
		return self.cursor.fetchall()

	def close(self):
		self.conn.close()


if __name__ == "__main__":
	db = DataBase()
	db.insert_sensor_modes('AHT21', ['temperature', 'humidity'])
	db.insert_sensor_modes('ENS160', ['eco2', 'tvoc', 'air_quality'])
	db.insert_sensor_modes('capacitive', ['moisture'])
	db.close()
	print("Database created")