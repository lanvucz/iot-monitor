import sqlite3
import uuid
import os
from datetime import date
from os import listdir
import csv


class SensorDatabase:

    def __init__(self, parent):
        self.update_message = parent.update_message
        self.conn = sqlite3.connect('db.sqlite3')
        self.cursorObj = self.conn.cursor()
        self.update_message("Database connected successfully")
        self.migration()
        self.uuid = None

    def migration(self):
        self.cursorObj.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='batch' ''')

        if not self.cursorObj.fetchone()[0] == 1:
            self.cursorObj.execute('''CREATE TABLE batch( 
                         operator           TEXT,
                         batch              TEXT,
                         date               TEXT,
                         sensors            TEXT,
                         uuid               TEXT
                         );''')
            self.update_message("Table BATCH created successfully")

        self.cursorObj.execute(
            ''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='sensor_record' ''')
        if not self.cursorObj.fetchone()[0] == 1:
            self.cursorObj.execute("CREATE TABLE sensor_record( \
                              sensor TEXT NOT NULL, \
                              timestamp INT, \
                              time TEXT, \
                              H REAL, \
                              D REAL,\
                              T REAL, \
                              M REAL, \
                              A REAL, \
                              uuid TEXT \
                              );")
            self.update_message("Table SENSOR_RECORD created successfully")

    def test_data(self):
        sql_tuples = [(1,11,11,22,22,22,22,22,'test'), (2,11,11,22,22,22,22,22,'test')]
        self.conn.executemany("INSERT INTO SENSOR_RECORD (sensor,timestamp,time,H,D,T,M,A,uuid) \
                     VALUES (?,?,?,?,?,?,?,?,?)", sql_tuples)
        self.conn.commit()

    def start_measurement(self):
        self.uuid = str(uuid.uuid4())
        if not self.check_connection():
            self.conn = sqlite3.connect('db.sqlite3')
            self.cursorObj = self.conn.cursor()

    def insert_sensor_record(self, data=[]):
        sql_tuples = []
        for d in data:
            sql_tuples.append((d["sensor"], d["timestamp"], d["time"], d["H"], d["D"], d["T"],
                               d["M"], d["A"],self.uuid))
        self.conn.executemany("INSERT INTO SENSOR_RECORD (sensor,timestamp,time,H,D,T,M,A,uuid) \
              VALUES (?,?,?,?,?,?,?,?,?)", sql_tuples)
        self.conn.commit()

    def get_batch_sensors_by_uuid(self, uuid):
        self.cursorObj.execute(
            f''' SELECT DISTINCT sensor FROM sensor_record WHERE uuid='{uuid}' ''')
        return self.cursorObj.fetchall()

    def query_sensor_record_by_uuid(self, uuid, limit=1000, offset=0):
        self.cursorObj.execute(f''' SELECT sensor,timestamp,time,H,D,T,M,A,uuid FROM sensor_record WHERE uuid='{uuid}' ORDER BY timestamp ASC LIMIT {limit} OFFSET {offset}''')
        return self.cursorObj.fetchall()

    def export_csv(self, uuid=None):
        if not os.path.exists('Results'):
            os.makedirs('Results')

        filename = date.today().strftime("%Y-%m-%d") # + "_" + str(self.batch)
        version = 0

        for f in listdir('Results'):
            if f.find(filename) != -1:
                version += 1

        if version != 0:
            filename = filename + '_' + str(version).zfill(3)

        # limit = 1000
        limit = 5
        offset = 0
        sensors =[str(s[0]) for s in self.get_batch_sensors_by_uuid(uuid=uuid)]
        keys = ["Real time", "Time"]
        for s in sensors:
            keys += [s+'-R', s+'-C', s+'-T']
        rows = self.query_sensor_record_by_uuid(uuid=uuid, limit=limit, offset=offset)
        print(len(rows))
        # timestamp_rows = {}
        # sensors = []
        # for row in rows:
        #     if not timestamp_rows[row.timestamp]:
        #         timestamp_rows[row.timestamp] =
        #
        #
        # keys = ["Real time", "Time"] + list(data.rawData.keys())
        #
        # with open("Results/" + filename + ".csv", "a", newline="") as csvfile:
        #     writer = csv.writer(csvfile)
        #     for row in rows:
        #
        #     for i in range(1, 7):
        #         writer.writerow(["S/N D" + str(i) + ":", str(data.devSN[i - 1])])
        #     writer.writerow(["Date: ", str(data.Date)])
        #     writer.writerow(["Batch: ", str(data.Batch)])
        #     writer.writerow(["Operator: ", str(data.Operator)])
        #     writer.writerow(keys)

    def stop_measurement(self):
        # self.conn.close()
        if self.check_connection():
            self.conn.close()

    def check_connection(self):
        try:
            self.conn.cursor()
            return True
        except Exception as e:
            return False