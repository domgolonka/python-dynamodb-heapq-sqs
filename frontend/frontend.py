#!/usr/bin/env python

'''
  CMPT 474-V0.5 ASSIGNMENT 3-BASICDB
'''

# Library packages
import os
import re
import sys
import json
import boto.sqs
import boto.sqs.message
import boto.dynamodb2

from boto.dynamodb2.items import Item
from boto.dynamodb2.fields import HashKey, RangeKey, KeysOnlyIndex, GlobalAllIndex
from boto.dynamodb2.table import Table
from boto.exception import JSONResponseError
from bottle import route, run, request, response, abort, default_app, HTTPResponse



AWS_REGION = "us-west-2"

REQ_ID_FILE = "reqid.txt"


# Instance naming
BASE_INSTANCE_NAME = "DB"

# Names for ZooKeeper hierarchy
APP_DIR = "/" + BASE_INSTANCE_NAME
PUB_PORT = "/Pub"
SUB_PORTS = "/Sub"
SEQUENCE_OBJECT = APP_DIR + "/SeqNum"
DEFAULT_NAME = BASE_INSTANCE_NAME + "1"
BARRIER_NAME = "/Ready"

# Publish and subscribe constants
SUB_TO_NAME = 'localhost' # By default, we subscribe to our own publications
BASE_PORT = 7777

AWS_REGION = "us-west-2"
WEB_PORT = 8080

RETDEL_QUERY_PATTERN = "^id=[0-9]|^name=[a-zA-Z_ ]"
ADD_ACTS_QUERY_PATTERN = "id=[0-9]+&activities=[a-zA-Z_ ]+[,a-zA-Z_ ]+"

def build_parser():
	''' Define parser for command-line arguments '''
	parser = argparse.ArgumentParser(description="Web server demonstrating final project technologies")
	parser.add_argument("zkhost", help="ZooKeeper host string (name:port or IP:port, with port defaulting to 2181)")
	parser.add_argument("web_port", type=int, help="Web server port number", nargs='?', default=WEB_PORT)
	parser.add_argument("name", help="Name of this instance", nargs='?', default=DEFAULT_NAME)
	parser.add_argument("number_dbs", type=int, help="Number of database instances", nargs='?', default=1)
	parser.add_argument("base_port", type=int, help="Base port for publish/subscribe", nargs='?', default=BASE_PORT)
	parser.add_argument("sub_to_name", help="Name of system to subscribe to", nargs='?', default=SUB_TO_NAME)
	parser.add_argument("proxy_list", help="List of instances to proxy, if any (comma-separated)", nargs='?', default="")
	return parser

def get_ports():
	''' Return the publish port and the list of subscribe ports '''
	db_names = [BASE_INSTANCE_NAME+str(i) for i in range(1, 1+args.number_dbs)]
	print db_names, args.proxy_list.split(',')
	if args.proxy_list != '':
		proxies = args.proxy_list.split(',')
	else:
		proxies = []
	return gen_ports.gen_ports(args.base_port, db_names, proxies, args.name)


def setup_pub_sub(zmq_context, sub_to_name):
	''' Set up the publish and subscribe connections '''
	global pub_socket
	global sub_sockets

	pub_port, sub_ports = get_ports()

	'''
		Open a publish socket. Use a 'bind' call.
	'''
	pub_socket = zmq_context.socket(zmq.PUB)
	'''
		The bind call does not take a DNS name, just a port.
	'''
	print "instance {0} binding on {1}".format(args.name, pub_port)
	pub_socket.bind("tcp://*:{0}".format(pub_port))

	sub_sockets = []
	for sub_port in sub_ports:
		'''
			Open a subscribe socket. Use a 'connect' call.
		'''
		sub_socket = zmq_context.socket(zmq.SUB)
		'''
          You always have to specify a SUBSCRIBE option, even
          in the case (such as this) where you are subscribing to
          every possible message (indicated by "").
		'''
		sub_socket.setsockopt(zmq.SUBSCRIBE, "")
		'''
          The connect call requires the DNS name of the system being
          subscribed to.
		'''
		print "instance {0} connecting to {1} on {2}".format(args.name, sub_to_name, sub_port)
		sub_socket.connect("tcp://{0}:{1}".format(sub_to_name, sub_port))
		sub_sockets.append(sub_socket)

@contextlib.contextmanager
def zmqcm(zmq_context):
	'''
      This function wraps a context manager around the zmq context,
      allowing the client to be used in a 'with' statement. Simply
      use the function without change.
	'''
	try:
		yield zmq_context
	finally:
		print "Closing sockets"
		# The "0" argument destroys all pending messages
		# immediately without waiting for them to be delivered
		zmq_context.destroy(0)

@contextlib.contextmanager
def kzcl(kz):
	'''
      This function wraps a context manager around the kazoo client,
      allowing the client to be used in a 'with' statement.  Simply use
      the function without change.
	'''
	kz.start()
	try:
		yield kz
	finally:
		print "Closing ZooKeeper connection"
		kz.stop()
		kz.close()


def getConn():
	try:
		conn = boto.sqs.connect_to_region(AWS_REGION)
		if conn == None:
			sys.stderr.write("Could not connect to AWS region '{0}'\n".format(AWS_REGION))
			sys.exit(1)

		my_q = conn.create_queue("sqs_in_queue")

	except Exception as e:
		sys.stderr.write("Exception connecting to SQS\n")
		sys.stderr.write(str(e))
		sys.exit(1)

	return my_q

def reqSend():
	global request_count

	request_count += 1
	req_file.seek(0)
	req_file.write(str(request_count))
	req_file.flush()
	os.fsync(req_file.fileno())

def main():
	'''
       Main routine. Initialize everything, wait
       for all the other instances to complete their
       initialization, then begin responding to requests.

       The following list of `global` statements are required
       by one of the more awkward parts of Python syntax: If you
       assign to a global variable anywhere inside a function, it
       is safest to declare that variable `global` at the
       top of the function.

       Strictly speaking, you don't have to do this in every 
       case, but it's simplest to just observe this rule and
       avoid mystifying bugs in the cases where it is required.

       If you're only *reading* a global variable inside a
       function, you don't need to declare it. For example,
       retrieve_route() doesn't declare `args` because it
       only reads that global variable.
	'''
	global args
	global table
	global seq_num
	global req_file
	global request_count

	# Get the command-line arguments
	parser = build_parser()
	args = parser.parse_args()

	# Set up the table
	table = table.open_table()

	# Initialize request id from durable storage
	if not os.path.isfile(REQ_ID_FILE):
		with open(REQ_ID_FILE, 'w', 0) as req_file:
			req_file.write("0\n")

	try:
		req_file = open(REQ_ID_FILE, 'r+', 0)
		request_count = int(req_file.readline())
    except IOError as exc:
		sys.stderr.write(
			"Exception reading request id file '{0}'\n".format(REQ_ID_FILE))
		sys.stderr.write(exc)
		sys.exit(1)

	# Open connection to ZooKeeper and context for zmq
	with kzcl(kazoo.client.KazooClient(hosts=args.zkhost)) as kz, \
		zmqcm(zmq.Context.instance()) as zmq_context:

		# Set up publish and subscribe sockets
		setup_pub_sub(zmq_context, args.sub_to_name)

		# Initialize sequence numbering by ZooKeeper
		if not kz.exists(SEQUENCE_OBJECT):
			kz.create(SEQUENCE_OBJECT, "0")
		else:
			kz.set(SEQUENCE_OBJECT, "0")

		# Wait for all DBs to be ready
		barrier_path = APP_DIR+BARRIER_NAME
		kz.ensure_path(barrier_path)
		b = kz.create(barrier_path + '/' + args.name, ephemeral=True)
		while len(kz.get_children(barrier_path)) < args.number_dbs:
			time.sleep(1)
		print "Past rendezvous"

        # Now the instances can start responding to requests

		'''
          Create the sequence counter.
          This creates client-side links to a common structure
          on the server side, so it has to be done *after* the
          rendezvous.
		'''
		seq_num = kz.Counter(SEQUENCE_OBJECT)

		'''
          Start the Web server.
          Because the server is running within the with block for the 
          ZooKeeper client, the connection to ZooKeeper will remain
          open for as long as the server runs. 

          To stop the server cleanly (ensuring cleanup of ZooKeeper and zmq),
          either use ^C (for a server running in the foreground) or
          `kill -2 <pid>` from the command line (for a server running
          in the background).  If you kill the server using any
          other signal than 2 (keyboard interrupt), ZooKeeper and zmq
          will not be cleaned up.  The other signals can be caught (and probably
          should in a production system) but the code to do so would complicate
          this demonstration.
		'''
		app = default_app()
		run(app, host="localhost", port=args.web_port)


@route('/delete')
def delete():
	import operations
	my_sqs = getConn()
	return operations.do_delete(my_sqs)

@route('/add_activities')
def add_activities():
	import operations
	my_sqs = getConn()
	return operations.do_add_activities(my_sqs)

@route('/retrieve')
def retrieve():
	import operations
	my_sqs = getConn()
	return operations.do_retrieve(my_sqs)

def getConn():
	try:
		conn = boto.sqs.connect_to_region(AWS_REGION)
		if conn == None:
			sys.stderr.write("Could not connect to AWS region '{0}'\n".format(AWS_REGION))
			sys.exit(1)

		my_q = conn.create_queue("sqs_in_queue")

	except Exception as e:
		sys.stderr.write("Exception connecting to SQS\n")
		sys.stderr.write(str(e))
		sys.exit(1)

	return my_q



    
