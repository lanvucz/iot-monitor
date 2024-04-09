from serial import Serial
import time
import os

if os.name == 'nt':
    serialPort = 'COM4'  # windows
else:
    serialPort = '/dev/ttyUSB0'  # linux

print('serialPort', serialPort)

ser = Serial(serialPort)
ser.baudrate = 9600
ser.bytesize = 8
ser.parity = 'N'
ser.stopbits = 1

data = bytearray(b'#01D\r')
print(data.decode('utf-8'))

No = ser.write(data)
print("write answer", No)

if ser.is_open:
    retry = 0
    while retry < 5:
        bytesToRead = ser.inWaiting()
        if bytesToRead:
            data = ser.read(bytesToRead)
            print(data, data.decode())
            break
        else:
            print('no data')
        time.sleep(1)
        retry += 1
else:
    print('serial not open')

ser.close()  # Close the Com port
