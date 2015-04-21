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
time.sleep(1)
os.system("curl 'http://localhost:8080/create?id=6&name=ali&activities=hi,bye'")
time.sleep(1)
os.system("curl 'http://localhost:8080/create?id=7&name=jug&activities=hi,bye'")
time.sleep(1)
#sleep(4)
os.system("curl 'http://localhost:8080/add_activities?id=4&activities=go,me'")
time.sleep(1)
os.system("curl 'http://localhost:8080/add_activities?id=6&activities=go,me'")
time.sleep(1)
os.system("curl 'http://localhost:8080/add_activities?id=90&activities=go,me,cars'")
time.sleep(1)
os.system("curl 'http://localhost:8080/retrieve?id=4'")
time.sleep(1)
os.system("curl 'http://localhost:8080/retrieve?name=ali'")
time.sleep(1)
os.system("curl 'http://localhost:8080/retrieve?name=arsalan'")
time.sleep(1)
os.system("curl 'http://localhost:8080/retrieve?id=305'")
time.sleep(1)
os.system("curl 'http://localhost:8080/delete?id=88'")
time.sleep(1)
os.system("curl 'http://localhost:8080/delete?name=jafar'")

os.system("curl 'http://localhost:8081/")
os.system("curl 'http://localhost:8081/")
os.system("curl 'http://localhost:8081/")
os.system("curl 'http://localhost:8081/")
os.system("curl 'http://localhost:8081/")
os.system("curl 'http://localhost:8081/")
os.system("curl 'http://localhost:8081/")
os.system("curl 'http://localhost:8081/")
os.system("curl 'http://localhost:8081/")
os.system("curl 'http://localhost:8081/")
os.system("curl 'http://localhost:8081/")
os.system("curl 'http://localhost:8081/")
os.system("curl 'http://localhost:8081/")
os.system("curl 'http://localhost:8081/")
os.system("curl 'http://localhost:8081/")
os.system("curl 'http://localhost:8081/")
os.system("curl 'http://localhost:8081/")
os.system("curl 'http://localhost:8081/")
os.system("curl 'http://localhost:8081/")
os.system("curl 'http://localhost:8081/")
os.system("curl 'http://localhost:8081/")
os.system("curl 'http://localhost:8081/")
os.system("curl 'http://localhost:8081/")
os.system("curl 'http://localhost:8081/")
os.system("curl 'http://localhost:8081/")
os.system("curl 'http://localhost:8081/")
os.system("curl 'http://localhost:8081/")
os.system("curl 'http://localhost:8081/")




#sleep(4)
#os.system("curl 'http://localhost:8080/retrieve?id=4'")
#sleep(4)
#os.system("curl 'http://localhost:8080/delete?id=4'")
#os.system("curl 'http://localhost:8080/?id=4'")
#os.system("curl 'http://localhost:8080/delete?id=4'")

