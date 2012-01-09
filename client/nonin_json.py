# -*- coding: iso-8859-15 -*-
# Developed by CareNet fall 2011. Compatible with Nonin 9560. 

import bluetooth
import logging
import time
import os
import sys
import threading
import time
import socket as sock
import json

#User name query possible here


HOST, PORT = "192.16.126.112", 9999
DEVICE_NAME = "NONIN"
LOG = logging.getLogger("nonin")
HOST_IS_DOWN_SIGNATURE = "Host is down"

class Nonin(object):
    
    def __init__(self):
        self.__connected = False
        self.__is_stopping = False
     

    def __connect(self):
        self.inet_sock = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
        self.inet_sock.connect((HOST, PORT))

        socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        address = "00:1C:05:00:46:AC"

        if address is not None:
            # There's saved BT address, try to connect
            try:
                LOG.debug("Connecting to saved BT address: %s" % address)
                socket.connect((address, 1))
                LOG.debug("Connected to saved BT address: %s" % address)
                return socket
            except bluetooth.BluetoothError, ex:
                if HOST_IS_DOWN_SIGNATURE in str(ex):
                    pass
                    # Saved BT address doesn't work, will do a scan
                else:
                    raise
                    
    
    def __decode(self, data):
        if len(data) == 4:
            #LOG.debug([bin(ord(i)) for i in data])
            #firstBlock = ord(data[0])<<7
            #firstBlockMasked = firstBlock&384
            #secondBlock = ord(data[1])
            #combinedBlock = firstBlockMasked|secondBlock
            return (((ord(data[0])<<7)&384)|ord(data[1])), ord(data[2])         
             
        
    def __listen(self, socket, results_receiver):
        #Line below needed if device has changed comms protocol
        #socket.send('\x02\x70\x02\x02\x08\x03')
        while not self.__is_stopping:
            data = socket.recv(60)
            heartRate, spo = self.__decode(data)            
            LOG.debug("Heartrate: " + str(heartRate) + ". SP02 level: " + str(spo) + ".")
            #self.inet_sock.send("elis"+":"+str(heartRate)+":"+str(spo))
            self.inet_sock.send(json.dumps({"hr": heartRate, "spo": spo, "patientId": "elis"}))            
            #results_receiver(hr, bat)

    def run(self, results_receiver=None):
        socket = self.__connect()
        if socket is None:
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
                

if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    def printer(hr, bat):
        print "Received HR: %d, bat: %d" % (hr, bat)
    n = Nonin()
    n.run(printer)
