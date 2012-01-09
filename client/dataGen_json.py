import socket as sock
import time
import random
import json

HOST, PORT = "192.16.126.112", 9999
#HOST, PORT = "127.0.0.1", 9999

inet_sock = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
inet_sock.connect((HOST, PORT))
hr = 100
high = 180
low = 60

while 1:
    #print hr
    inet_sock.send(json.dumps({"hr": int(hr), "spo": 99, "patientId": "elis"}))
    print json.dumps({"hr": int(hr), "spo": 99, "patientId": "elis"})
    hr += random.normalvariate(0, 2)
    if (hr<low):
        hr = low
    if (hr>high):
        hr = high 
    time.sleep(1)

