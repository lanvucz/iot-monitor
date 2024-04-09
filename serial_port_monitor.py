import serial, time, threading


class SerialPortMonitor(threading.Thread):
    def __init__(self,
                 data_output_queue, error_message_queue,
                 serial_port_number,
                 com_measurement_symbol="H",
                 time_interval=60,
                 baudrate=9600,
                 bytesize=serial.EIGHTBITS,
                 parity=serial.PARITY_NONE,
                 stopbits=serial.STOPBITS_ONE,
                 timeout=0.01
                 ):
        threading.Thread.__init__(self)

        self.connection_attributes = dict(port=serial_port_number,
                                          baudrate=baudrate,
                                          bytesize=bytesize,
                                          stopbits=stopbits,
                                          parity=parity,
                                          timeout=timeout
                                          )
        self.serial_connection = None
        self.address = None
        self.com_command = None
        self.start_time = None
        self.time_sleep = time_interval
        self.measurement_symbol = com_measurement_symbol
        self.data_queue = data_output_queue
        self.error_queue = error_message_queue
        self.alive = threading.Event()
        self.alive.set()

    def connect(self):
        try:
            if self.serial_connection:
                self.serial_connection.close()
            self.serial_connection = serial.Serial(**self.connection_attributes)
        except serial.SerialException as e:
            print('Failed to connect to serial port.', e)
            self.error_queue.put(str(e))
            return

    def clean(self):
        if self.serial_connection:
            self.serial_connection.close()

    def write(self, command):
        self.serial_connection.write(command)

    def read(self):
        if self.serial_connection.is_open:
            retry = 0
            while retry < 5:
                bytes_to_read = self.serial_connection.inWaiting()
                if bytes_to_read:
                    data = self.serial_connection.read(bytes_to_read)
                    return data.decode()
                # else:
                #     print('wait for data...')
                time.sleep(1)
                retry += 1
        else:
            print('Serial port not open.')
        return None

    def get_command(self, address=None):
        text = '#{}{}\r'.format(address or self.address, self.measurement_symbol)
        return bytearray(str.encode(text))

    def read_address(self):
        try:
            for i in range(0x00, 0x0A):
                address = str(i).zfill(2)
                command = self.get_command(address)
                if self.test_connection(command) is not None:
                    self.address = address
                    return address
                time.sleep(1)
        except NameError:
            print("Device not connected!")
        except AttributeError:
            print("Device not connected!")
        except OSError:
            print("Device not connected. Possible error.")
        self.error_queue.put("Failed to find address.")
        return None

    def test_connection(self, command):
        self.write(command)
        return self.read()

    def run(self):
        self.connect()
        if not self.serial_connection:
            return
        address = self.read_address()
        if not address:
            return
        self.com_command = self.get_command()

        # Restart the clock
        self.start_time = time.time()

        while self.alive.isSet():
            self.write(self.com_command)
            data = self.read()
            timestamp = time.time()
            time_from_start = (timestamp - self.start_time)
            # print(timestamp, data)
            self.data_queue.put((data, int(timestamp), time_from_start))
            time.sleep(self.time_sleep)

        self.clean()

    def join(self, timeout=None):
        self.alive.clear()
        threading.Thread.join(self, timeout)
