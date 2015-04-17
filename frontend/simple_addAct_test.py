# to use this script, do this in the terminal
# (make sure simple.py is in current directory)
# $ python simple.py

import os, time
'''
def sleep(sec):
	print "sleeping..."
	for x in range(sec):
		print "tick"
		time.sleep(1)
'''
os.system("curl 'http://localhost:8080/add_activities?id=4&activities=basketball'")

'''
print "1: "
os.system("curl 'http://localhost:8080/create?id=4&name=ali&activities=hi,bye'")
sleep(5)
os.system("curl 'http://localhost:8080/create?id=10&name=ethic&activities=go,me'")
'''
