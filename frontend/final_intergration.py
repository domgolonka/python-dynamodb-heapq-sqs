# to use this script, do this in the terminal
# (make sure simple.py is in current directory)
# $ python simple.py

import os, time

def sleep(sec):
	print "sleeping..."
	for x in range(sec):
		print "tick"
		time.sleep(1)

os.system("curl 'http://localhost:8080/create?id=4&name=ali&activities=hi,bye'")
#sleep(4)
os.system("curl 'http://localhost:8080/add_activities?id=4&activities=go,me'")
#sleep(4)
os.system("curl 'http://localhost:8080/retrieve?id=4'")
#sleep(4)
os.system("curl 'http://localhost:8080/delete?id=4'")
#os.system("curl 'http://localhost:8080/?id=4'")
#os.system("curl 'http://localhost:8080/delete?id=4'")

