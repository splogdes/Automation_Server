import sqlite3


class DataBase:

    def __init__(self, db_name = 'data.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()


    def insert_sensor_data(self, timestamp, mac_address, temperature = None, humidity = None):
        self.cursor.execute('''INSERT INTO sensor_data (timestamp, temperature, humidity, mac_address) 
                        VALUES(?,?,?,?)''', (timestamp, temperature, humidity, mac_address))
        self.conn.commit()

    def insert_soil_data(self, timestamp, mac_address, soil_moisture = None):
        self.cursor.execute('''INSERT INTO soil_data (timestamp, soil_moisture, mac_address) 
                        VALUES(?,?,?)''', (timestamp, soil_moisture, mac_address))
        self.conn.commit()

    def insert_device(self, mac_address, ip_address, model = None, location = None):
        self.cursor.execute('''INSERT INTO devices (mac_address,ip_address, model, location) 
                        VALUES(?,?,?,?)''', (mac_address, ip_address, model, location))
        self.conn.commit()

    def update_device(self, mac_address, ip_address, model, location):
        self.cursor.execute('''UPDATE devices SET ip_address = ?, model = ?, location = ? WHERE mac_address = ?''', (ip_address, model, location, mac_address))
        self.conn.commit()

    def insert_sensors(self, mac_address, name, model):
        self.cursor.execute('''INSERT INTO sensors (mac_address, name, model) 
                        VALUES(?,?,?)''', (mac_address, name, model))
        self.conn.commit()

    def is_device_registered(self, mac_address):
        self.cursor.execute('''SELECT * FROM devices WHERE mac_address = ?''', (mac_address,))
        return self.cursor.fetchone() is not None
    
    def get_device(self, mac_address):
        self.cursor.execute('''SELECT * FROM devices WHERE mac_address = ?''', (mac_address,))
        return self.cursor.fetchone()
    
    def get_devices(self):
        self.cursor.execute('''SELECT * FROM devices''')
        return self.cursor.fetchall()
    
    def get_sensors(self, mac_address):
        self.cursor.execute('''SELECT name,model FROM sensors WHERE mac_address = ?''', (mac_address,))
        return self.cursor.fetchall()
    
    def get_sensor_data(self, mac_address, start, end):
        self.cursor.execute('''SELECT temperature,humidity FROM sensor_data WHERE mac_address = ? AND timestamp >= ? AND timestamp <= ?''', (mac_address, start, end))
        return self.cursor.fetchall()
    
    def get_soil_data(self, mac_address, start, end):
        self.cursor.execute('''SELECT soil_moisture FROM soil_data WHERE mac_address = ? AND timestamp >= ? AND timestamp <= ?''', (mac_address, start, end))
        return self.cursor.fetchall()
    
    def get_sensor_data_last_n(self, mac_address, n):
        self.cursor.execute('''SELECT temperature,humidity FROM sensor_data WHERE mac_address = ? ORDER BY timestamp DESC LIMIT ?''', (mac_address, n))
        return self.cursor.fetchall()
    
    def get_soil_data_last_n(self, mac_address, n):
        self.cursor.execute('''SELECT soil_moisture FROM soil_data WHERE mac_address = ? ORDER BY timestamp DESC LIMIT ?''', (mac_address, n))
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()

    def create_table(self):

        self.cursor.execute(''' CREATE TABLE IF NOT EXISTS
                        devices(
                        mac_address VARCHAR(17) PRIMARY KEY,
                        ip_address TEXT NOT NULL,
                        model TEXT,
                        location TEXT
                        )''')


        self.cursor.execute(''' CREATE TABLE IF NOT EXISTS 
                        sensor_data( 
                        timestamp TIMESTAMP PRIMARY KEY,
                        temperature FLOAT,
                        humidity FLOAT,
                        mac_address VARCHAR(17),
                        FOREIGN KEY(mac_address) REFERENCES devices(mac_address)
                        )''')

        self.cursor.execute(''' CREATE TABLE IF NOT EXISTS 
                        soil_data( 
                        timestamp TIMESTAMP PRIMARY KEY,
                        soil_moisture INTEGER,
                        mac_address VARCHAR(17),
                        FOREIGN KEY(mac_address) REFERENCES devices(mac_address)
                        )''')


        self.conn.execute(''' CREATE TABLE IF NOT EXISTS
                        sensors(
                        mac_address VARCHAR(17),
                        name TEXT,
                        model TEXT,
                        PRIMARY KEY(mac_address, name),
                        FOREIGN KEY(mac_address) REFERENCES devices(mac_address)
                        )''')

        self.conn.commit()