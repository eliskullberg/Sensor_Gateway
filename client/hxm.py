# -*- coding: iso-8859-15 -*-
# HXM BT message decoding adapted from HXM Tracker by Jari Multisilta
#  http://www.my-maemo.com/software/applications.php?name=HXM_Tracker&faq=38&fldAuto=1293

import bluetooth
import logging
import time
import os
import sys
import threading
import time
import socket as sock

HOST, PORT = "localhost", 9990
DEVICE_NAME = "HXM"
LOG = logging.getLogger("hxm")
HOST_IS_DOWN_SIGNATURE = "Host is down"

class HXM(object):
    
    def __init__(self):
        self.__connected = False
        self.__is_stopping = False

    def __read_config(self):
        path = os.path.expanduser("~/.hxmpref.txt")
        if os.path.exists(path):
            btaddr = open(path).read().strip() 
            LOG.info("Got BT address from %s" % path)
            return btaddr

    def __write_config(self, address):
        path = os.path.expanduser("~/.hxmpref.txt")
        with open(path, "w") as f:
            f.write(address)
        
        LOG.debug("Wrote BT address to %s" % path)
        
    def __lookup_bt_address(self):
        max_tries = 2
        tries = 0
        while tries < max_tries and not self.__is_stopping:
            tries += 1
            LOG.info("Scanning bluetooth devices... (try %d of %d)" \
                     % (tries, max_tries))

            for addr, name in bluetooth.discover_devices(lookup_names=True):
                LOG.info("Found device: %s (%s)" % (name, addr))
                if name is not None and name.startswith(DEVICE_NAME):
                    return addr

    def __connect(self):
        """ Connect to HXM, return socket or None on failure. 
        
        If there's saved BT address in ~/.hxmpref.txt, use it.
        If there's no saved BT address or the host is down, do a scan for 
        BT devices. 
        
        """

        self.inet_sock = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
        self.inet_sock.connect((HOST, PORT))
        socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

        address = self.__read_config()
        if address is not None:
            # There's saved BT address, try to connect
            try:
                LOG.debug("Connecting to saved BT address: %s" % address)
                socket.connect((address, 1))
                return socket
            except bluetooth.BluetoothError, ex:
                if HOST_IS_DOWN_SIGNATURE in str(ex):
                    pass
                    # Saved BT address doesn't work, will do a scan
                else:
                    raise
                    
        # Didn't get usable BT address from config, do a scan
        
        address = self.__lookup_bt_address()
        if address is None:
            LOG.info("No usable BT devices found")
            return None

        
        # Found HXM! Now save its address for faster
        # future startups
        self.__write_config(address)

        LOG.debug("Connecting to BT address from scan: %s" % address)
        socket.connect((address, 1))
        return socket
    
    def __decode(self, data):
        
        if len(data) != 58:
            #LOG.debug("__decode, len(data) != 59, ignoring frame")
            return None, None
        
        if ord(data[1]) != 32:
            #LOG.debug("__decode, data[1] != 55, ignoring frame")
            return None, None
        
        self.inet_sock.send(data + "\n")
        print [ord(i) for i in data]
        print ord(data[12])
        return None, None
        
        # Heart beat, valid range 30..240
        hr = ord(data[12])
        
        # Battery index, 0..100%
        bat = 100
        
        if hr < 30 or hr > 240:
            LOG.debug("__decode, HR=%d, ignoring frame" % hr)
            return None, None 

        if bat < 0 or bat > 100:
            LOG.debug("__decode, bat=%d, ignoring frame" % bat)
            return None, None 
        
        return hr, bat
        
    def __listen(self, socket, results_receiver):
        socket.send('\x02\x14\x01\x01\x5e\x03')
        while not self.__is_stopping:
            socket.send('\x02\x14\x01\x01\x5e\x03')
            data = socket.recv(60)
            hr, bat = self.__decode(data)
            if results_receiver and hr and bat:
                LOG.debug("Sending HR: %s, Bat: %s" % (hr, bat))
                results_receiver(hr, bat)

    def run(self, results_receiver=None):
        socket = self.__connect()
        if socket is None:
            # Assume the HXM is connectable on startup.
            # If we cannot connect on startup, give up immediately.
            return
        
        
        
        while not self.__is_stopping:
            try:
                while socket is None and not self.__is_stopping:
                    # If self.__connect() is failing immediately,
                    # we want to wait for a bit before trying again
                    time.sleep(1)
                    # Inform results receiver that we have 
                    # a connectivity issue
                    results_receiver(None, None)
                    socket = self.__connect()
            
                self.__listen(socket, results_receiver)

            except bluetooth.BluetoothError, ex:
                LOG.exception("Bluetooth error, will try to reconnect")
                socket = None

    def stop(self):
        """ Signal run() to return as soon as possible. """
        
        self.__is_stopping = True
                

class HXMThread(threading.Thread):
    def __init__(self, results_receiver):
        threading.Thread.__init__(self)
        self.__results_receiver = results_receiver
        self.__hxm = HXM()
    
    def run(self):
        self.__hxm.run(self.__results_receiver)
        
    def stop(self):
        self.__hxm.stop()

if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    def printer(hr, bat):
        print "Received HR: %d, bat: %d" % (hr, bat)
    
    hxm = HXM()
    hxm.run(printer)
