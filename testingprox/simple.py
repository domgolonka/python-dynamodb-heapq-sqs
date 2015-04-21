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
os.system("curl 'http://localhost:8080/retrieve?id=1'")
time.sleep(1)
os.system("curl 'http://localhost:8080/retrieve?id=2'")
time.sleep(1)
os.system("curl 'http://localhost:8080/retrieve?id=3'")
time.sleep(1)
os.system("curl 'http://localhost:8080/retrieve?id=4'")
time.sleep(1)
os.system("curl 'http://localhost:8080/retrieve?id=5'")
time.sleep(1)
os.system("curl 'http://localhost:8080/retrieve?id=6'")
time.sleep(1)


'''
print "1: "
os.system("curl 'http://localhost:8080/create?id=4&name=ali&activities=hi,bye'")
sleep(5)
os.system("curl 'http://localhost:8080/create?id=10&name=ethic&activities=go,me'")
'''
