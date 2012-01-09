import SocketServer
import rrdtool
from time import time
import os
import commands
import logging
import json

PATH_TO_BASE = "/var/www/"
LOG = None

class MyTCPHandler(SocketServer.BaseRequestHandler):


    def checkExists(self, filename):
        try:
            open(PATH_TO_BASE + "rrds/" + filename)
        except IOError as e:
            #rrdtool create nonin.rrd --start 1323169750 --step 1 DS:hr:GAUGE:30:0:256 DS:sp:GAUGE:30:0:256 RRA:LAST:0.5:1:60 RRA:AVERAGE:0.5:60:60
            ret = rrdtool.create(PATH_TO_BASE + "rrds/" + filename, "--step", "1", "--start", str(int(time())), "DS:hr:GAUGE:30:0:256", "DS:sp:GAUGE:30:0:256", "RRA:LAST:0.5:1:3600", "RRA:LAST:0.5:60:86400") 
            LOG.warning("created new www directory and rrd as " + filename)


    def handle(self):
        self.input = "1"
        LOG.warning("ACtually doing studff")
        while (True and self.input != ""):
            try:
                self.input = self.request.recv(1024).strip()             
                self.data = json.loads(self.input)
            except ValueError:
                LOG.warning("Data is :" + str(self.input))
                LOG.warning("Empty Json object found, prob EOF")
                break
                
            if (len(self.data) == 3):
                self.patientId = str(self.data['patientId'])
                hr = str(self.data['hr'])
                sp = str(self.data['spo'])
                filename = self.patientId + ".rrd"
                self.checkExists(filename)
                LOG.warning("updating database with " + hr + sp)
                ret1 = rrdtool.update(PATH_TO_BASE + "rrds/" + filename,"N:"+hr+":"+sp)
            else:
                LOG.warning("Skipping malformatted data package")
                LOG.warning(self.data)
        
  

if __name__ == "__main__":
    HOST, PORT = "192.16.126.112", 9999
    #HOST, PORT = "127.0.0.1", 9999

    LOG = logging.getLogger('sensor_server')
    hdlr = logging.FileHandler('/var/tmp/sensor_server.log')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    LOG.addHandler(hdlr) 
    LOG.setLevel(logging.WARNING)
    

    #Create the server, binding to localhost on port 9999
    server = SocketServer.ThreadingTCPServer((HOST, PORT), MyTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
