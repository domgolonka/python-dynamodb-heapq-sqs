import kazoo.client
import contextlib
import time

class OperationSequencer:

	def __init__(self, kz, db_name, num_dbs):

		self.kz = kz
		self.db_name = db_name		
		self.num_dbs = num_dbs

		self.APP_DIR = "/group-tooMuchCoffeeTest"
		self.SEQUENCE_OBJECT = APP_DIR + "/SeqNum"

		self.BARRIER_NAME = "/Ready"
		self.BARRIER_PATH = self.APP_DIR + self.BARRIER_NAME

	  	# Initialize sequence numbering by ZooKeeper  
	  	if not self.kz.exists(SEQUENCE_OBJECT):
    		self.kz.create(SEQUENCE_OBJECT, "0")
	  	else:
	    	self.kz.set(SEQUENCE_OBJECT, "0")

		#wait for all DBs to be ready
		self.kz.ensure_path(self.BARRIER_PATH)

		#create node for the db instance
		b = self.kz.create(self.BARRIER_PATH + '/' + self.db_name, ephemeral=True)
		while len(self.kz.get_children(self.BARRIER_PATH)) < self.num_dbs:
		    time.sleep(1)
		#DBs are all ready now
		print "Past rendezvous"

		self.seq_num = self.kz.Counter(self.SEQUENCE_OBJECT)

	def sequence(self, operation, id):
		children = kz.get_children(kz.BARRIER_PATH)
