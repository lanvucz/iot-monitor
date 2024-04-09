import os, serial, glob, queue


############################################################################
def enumerate_serial_ports():
    """
    Purpose:        scan for available serial ports
    Return:         return a list of of the available ports names
    """
    if os.name == 'nt':
        available_ports = []
        for i in range(256):
            try:
                s = serial.Serial("COM{}".format(i))
                available_ports.append(s.portstr)
                s.close()
            except serial.SerialException:
                pass
        return available_ports
    else:
        return glob.glob('/dev/tty.*')


############################################################################

def get_item_from_queue(Q, timeout=0.01):
    """ Attempts to retrieve an item from the queue Q. If Q is
        empty, None is returned.

        Blocks for 'timeout' seconds in case the queue is empty,
        so don't use this method for speedy retrieval of multiple
        items (use get_all_from_queue for that).
    """
    try:
        item = Q.get(True, timeout)
    except queue.Empty:
        return None
    return item


############################################################################
def get_all_from_queue(Q):
    """ Generator to yield one after the others all items
        currently in the queue Q, without any waiting.
    """
    try:
        while True:
            yield Q.get_nowait()
    except queue.Empty:
        return None
############################################################################