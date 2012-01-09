#!/usr/bin/python
import rrdtool
import cgi
import cgitb
import sys
import os

cgitb.enable()

form = cgi.FieldStorage()

PATH_TO_BASE = "/var/www/"

print "Content-Type: text/plain;"
#print "Content-Type: text/html;"
print 


##Some type of sanity check needed
if (not form.has_key("time") or not form.has_key("timeUnit") or not form.has_key("patientId") or not form.has_key("patientId")):
    print open(PATH_TO_BASE + "sadface3.png", "rb").read()
    sys.exit()
patientId = form.getfirst("patientId", "")
timeUnit = form.getfirst("timeUnit", "")
time = form.getfirst("time","" )

hr, spo = (False, False)
if (form.has_key("spo2")):
    spo = True
if (form.has_key("hr")):
    hr = True

fullTime = time + timeUnit


filename = PATH_TO_BASE + "rrds/" + patientId + ".rrd"

if (spo == True and hr == True):
    f =os.popen('rrdtool xport --start -' + fullTime + ' --end now DEF:hr='+filename+':hr:LAST DEF:sp='+ filename+':sp:LAST XPORT:hr:"heart rate" XPORT:sp:"SPO2 level"')    
#elif (spo == True):
#elif (hr == True):
#else:

for i in f.readlines():
     print i,
print "123123123"

