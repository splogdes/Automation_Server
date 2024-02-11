import sqlite3


class DataBase:

    def __init__(self, db_name = 'data.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()


    def insert_sensor_data(self, timestamp, mac_address, temperature = None, humidity = None):
        self.cursor.execute('''INSERT INTO SENSOR_DATA (timestamp, temperature, humidity, mac_address) 
                        VALUES(?,?,?,?)''', (timestamp, temperature, humidity, mac_address))
        self.conn.commit()

    def insert_soil_data(self, timestamp, mac_address, soil_moisture = None):
        self.cursor.execute('''INSERT INTO SOIL_DATA (timestamp, soil_moisture, mac_address) 
                        VALUES(?,?,?)''', (timestamp, soil_moisture, mac_address))
        self.conn.commit()

    def insert_device(self, mac_address, addr, model = None, location = None):
        self.cursor.execute('''INSERT INTO DEVICES (mac_address, ip_address, port, model, location) 
                        VALUES(?,?,?,?,?)''', (mac_address, addr[0], addr[1], model, location))
        self.conn.commit()

    def update_device(self, mac_address, addr, model, location):
        self.cursor.execute('''UPDATE DEVICES SET ip_address = ?, port = ?, model = ?, location = ? WHERE mac_address = ?''', (addr[0], addr[1], model, location, mac_address))
        self.conn.commit()

    def insert_sensors(self, mac_address, name, model):
        self.cursor.execute('''INSERT INTO SENSORS (mac_address, name, model) 
                        VALUES(?,?,?)''', (mac_address, name, model))
        self.conn.commit()

    def is_device_registered(self, mac_address):
        self.cursor.execute('''SELECT * FROM DEVICES WHERE mac_address = ?''', (mac_address,))
        return self.cursor.fetchone() is not None
    
    def get_device_ip(self, mac_address):
        self.cursor.execute('''SELECT ip_address , port FROM DEVICES WHERE mac_address = ?''', (mac_address,))
        return self.cursor.fetchone()

    def get_device(self, mac_address):
        self.cursor.execute('''SELECT * FROM DEVICES WHERE mac_address = ?''', (mac_address,))
        return self.cursor.fetchone()
    
    def get_devices(self):
        self.cursor.execute('''SELECT * FROM DEVICES''')
        return self.cursor.fetchall()
    
    def get_sensors(self, mac_address):
        self.cursor.execute('''SELECT name,model FROM SENSORS WHERE mac_address = ?''', (mac_address,))
        return self.cursor.fetchall()
    
    def get_sensor_data(self, mac_address, start, end):
        self.cursor.execute('''SELECT temperature,humidity FROM SENSOR_DATA WHERE mac_address = ? AND timestamp >= ? AND timestamp <= ?''', (mac_address, start, end))
        return self.cursor.fetchall()
    
    def get_soil_data(self, mac_address, start, end):
        self.cursor.execute('''SELECT soil_moisture FROM SOIL_DATA WHERE mac_address = ? AND timestamp >= ? AND timestamp <= ?''', (mac_address, start, end))
        return self.cursor.fetchall()
    
    def get_sensor_data_last_n(self, mac_address, n):
        self.cursor.execute('''SELECT temperature,humidity FROM SENSOR_DATA WHERE mac_address = ? ORDER BY timestamp DESC LIMIT ?''', (mac_address, n))
        return self.cursor.fetchall()
    
    def get_soil_data_last_n(self, mac_address, n):
        self.cursor.execute('''SELECT soil_moisture FROM SOIL_DATA WHERE mac_address = ? ORDER BY timestamp DESC LIMIT ?''', (mac_address, n))
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()

    def create_table(self):

        self.cursor.execute(''' CREATE TABLE IF NOT EXISTS
                        DEVICES(
                        mac_address VARCHAR(17) PRIMARY KEY,
                        ip_address VARCHAR(15) NOT NULL,
                        port INTEGER,
                        model VARCHAR(50),
                        location VARCHAR(50)
                        )''')


        self.cursor.execute(''' CREATE TABLE IF NOT EXISTS 
                        SENSOR_DATA( 
                        MESSAGE_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TIMESTAMP,
                        temperature FLOAT,
                        humidity FLOAT,
                        mac_address VARCHAR(17),
                        FOREIGN KEY(mac_address) REFERENCES DEVICES(mac_address)
                        )''')

        self.cursor.execute(''' CREATE TABLE IF NOT EXISTS 
                        SOIL_DATA( 
                        MESSAGE_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TIMESTAMP,
                        soil_moisture INTEGER(8),
                        mac_address VARCHAR(17),
                        FOREIGN KEY(mac_address) REFERENCES DEVICES(mac_address)
                        )''')


        self.conn.execute(''' CREATE TABLE IF NOT EXISTS
                        SENSORS(
                        mac_address VARCHAR(17),
                        name VARCHAR(50),
                        model VARCHAR(50),
                        PRIMARY KEY(mac_address, name),
                        FOREIGN KEY(mac_address) REFERENCES DEVICES(mac_address)
                        )''')
        
        self.conn.execute(''' CREATE VIEW IF NOT EXISTS
                          LAST_CONNECTION AS
                          SELECT mac_address, MAX(timestamp) AS last_message FROM (
                          SELECT mac_address , timestamp FROM sensor_data UNION SELECT mac_address , timestamp FROM soil_data)
                          GROUP BY mac_address;''')

        self.conn.commit()