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
                    CREATE TABLE IF NOT EXISTS DEVICES(
                        mac_address VARCHAR(17) PRIMARY KEY,
                        ip_address VARCHAR(15) NOT NULL,
                        port INTEGER(5) NOT NULL,
                        model VARCHAR(50),
                        location VARCHAR(50)
                    )''')

        self.conn.execute('''
                    CREATE TABLE IF NOT EXISTS SENSORS(
                        sensor_name VARCHAR(50),
                        mac_address VARCHAR(17),
                        type VARCHAR(50),
                        model VARCHAR(50),
                        PRIMARY KEY(mac_address, sensor_name),
                        FOREIGN KEY(mac_address) REFERENCES DEVICES(mac_address)
                    )''')
        

        self.conn.execute(''' 
                    CREATE TABLE IF NOT EXISTS MESSAGES(
                        message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        mac_address VARCHAR(17),
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY(mac_address) REFERENCES DEVICES(mac_address)
                    )''')
        
        self.conn.execute(''' CREATE TABLE IF NOT EXISTS SENSOR_DATA(
                        did INTEGER PRIMARY KEY AUTOINCREMENT,
                        message_id INTEGER,
                        sensor_name INTEGER,
                        value DOUBLE,
                        FOREIGN KEY(message_id) REFERENCES MESSAGES(message_id),
                        FOREIGN KEY(sensor_name) REFERENCES SENSORS(sensor_name)
                    )''')

        self.conn.commit()

    def insert_device(self, mac_address, ip_address, port, model, location):
        self.cursor.execute(
            '''INSERT INTO DEVICES(mac_address, ip_address, port, model, location) VALUES(?,?,?,?,?)''',
            (mac_address, ip_address, port, model, location)
            )
        self.conn.commit()

    def insert_sensor(self, mac_address, sensor_name, type, model):
        self.cursor.execute(
            '''INSERT INTO SENSORS(mac_address, sensor_name, type, model) VALUES(?,?,?,?)''',
            (mac_address, sensor_name, type, model)
            )
        self.conn.commit()

    def insert_message(self, mac_address, data : list = None):
        if data is None:
            data = {}
        self.cursor.execute('''INSERT INTO MESSAGES(mac_address) VALUES(?)''', (mac_address,))
        message_id = self.cursor.lastrowid
        for sensor, value in data.items():
            self.cursor.execute(
                '''INSERT INTO SENSOR_DATA(message_id, sensor_name, value) VALUES(?,?,?)''',
                (message_id, sensor, value)
                )
        self.conn.commit()

    def is_device_registered(self, mac_address):
        self.cursor.execute('''SELECT * FROM DEVICES WHERE mac_address = ?''', (mac_address,))
        return self.cursor.fetchone() is not None
    
    def is_sensor_registered(self, mac_address, sensor_name):
        self.cursor.execute('''
                            SELECT * FROM SENSORS WHERE (sensor_name = ? AND mac_address=?)''',
                            (sensor_name, mac_address)
                            )
        return self.cursor.fetchone() is not None
    
    def update_device(self, mac_address, ip_address, port, model, location):
        self.cursor.execute('''
                            UPDATE DEVICES SET ip_address = ?, port = ?, model = ?, location = ? WHERE mac_address = ?''',
                            (ip_address, port, model, location, mac_address)
                            )
        self.conn.commit()

    def close(self):
        self.conn.close()
