#!/usr/bin/python
import rrdtool
import cgi
import cgitb
import sys

cgitb.enable()

form = cgi.FieldStorage()

PATH_TO_BASE = "/var/www/"

print "Content-Type: image/png;"
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
    ret2 = rrdtool.graph( PATH_TO_BASE + "pngs/" + patientId+".png", "--start", "-" +fullTime , "--vertical-label=pulse/spo2", "DEF:heartrate="+filename+":hr:LAST", "LINE1:heartrate#0000FF:heart rate\\r","DEF:spo="+filename+":sp:LAST", "LINE2:spo#FF0000:SPO2 level\\r", "CDEF:hsquare=heartrate,8,*", "CDEF:ssquare=spo,8,*")
elif (spo == True):
    ret2 = rrdtool.graph( PATH_TO_BASE + "pngs/" + patientId+".png", "--start", "-" +fullTime , "--vertical-label=spo2", "DEF:spo="+filename+":sp:LAST", "LINE1:spo#FF0000:SPO2 level\\r",  "CDEF:ssquare=spo,8,*")  
elif (hr == True):
    ret2 = rrdtool.graph( PATH_TO_BASE + "pngs/" + patientId+".png", "--start", "-" +fullTime , "--vertical-label=pulse", "DEF:heartrate="+filename+":hr:LAST", "LINE1:heartrate#0000FF:heart rate\\r", "CDEF:hsquare=heartrate,8,*")
else:
    ret2 = rrdtool.graph( PATH_TO_BASE + "pngs/" + patientId+".png", "--start", "-0s" , "--vertical-label=pulse/spo2", "DEF:heartrate="+filename+":hr:LAST", "LINE1:heartrate#0000FF:no data to graph\\r")


print open(PATH_TO_BASE + "pngs/" + patientId+".png", "rb").read()



