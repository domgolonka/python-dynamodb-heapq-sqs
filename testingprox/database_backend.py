#!/usr/bin/env python

# Standard library packages
import sys
import json
import time
import signal
import os.path
import argparse
import contextlib

import boto.sqs
import boto.sqs.message
import boto.dynamodb2

import heapq
import heap


from boto.dynamodb2.items import Item
from boto.dynamodb2.fields import HashKey, RangeKey, KeysOnlyIndex, GlobalAllIndex
from boto.dynamodb2.table import Table
from boto.exception import JSONResponseError

import DB

# Installed packages

import zmq

import kazoo.exceptions

from bottle import route, run, request, response, abort, default_app

# Local modules
#import table
#import retrieve
import gen_ports
import kazooclientlast

REQ_ID_FILE = "reqid.txt"


AWS_REGION = "us-west-2"

WEB_PORT = 8080

# Instance naming
BASE_INSTANCE_NAME = "DB"

# Names for ZooKeeper hierarchy
APP_DIR = "/ali/" + BASE_INSTANCE_NAME
PUB_PORT = "/Pub"
SUB_PORTS = "/Sub"
SEQUENCE_OBJECT = APP_DIR + "/SeqNum"
DEFAULT_NAME = BASE_INSTANCE_NAME + "1"
BARRIER_NAME = "/Ready"

DEFAULT_INPUT_SQS_NAME = "input_SQS"
DEFAULT_OUTPUT_SQS_NAME = "output_SQS"




# Publish and subscribe constants
SUB_TO_NAME = 'localhost' # By default, we subscribe to our own publications
BASE_PORT = 7777

def build_parser():
    ''' Define parser for command-line arguments '''
    parser = argparse.ArgumentParser(description="The database backend")
    parser.add_argument("zkhost", help="ZooKeeper host string (name:port or IP:port, with port defaulting to 2181)",nargs='?',default="cloudsmall1.cs.surrey.sfu.ca")
    parser.add_argument("inSQS_name", help="name of input queue", nargs='?', default="inque")
    parser.add_argument("outSQS_name", help="name of output queue", nargs='?', default="outque")
    parser.add_argument("name_all", help="Name of this instance", nargs='?', default=DEFAULT_NAME)
    parser.add_argument("base_port", type=int, help="Base port for publish/subscribe", nargs='?', default=BASE_PORT)
    parser.add_argument("name", help="Name of this instance", nargs='?', default=DEFAULT_NAME)
    parser.add_argument("number_dbs", type=int, help="Number of database instances", nargs='?', default=2)
    parser.add_argument("sub_to_name", help="List of instances to proxy, if any (comma-separated)", nargs='?', default="localhost")
    parser.add_argument("proxy_list", help="List of instances to proxy, if any (comma-separated)", nargs='?', default="")
 	
    return parser

def get_ports():
    ''' Return the publish port and the list of subscribe ports '''
    db_names = dbname_a
    print db_names, args.proxy_list.split(',')
    print  db_names
    print db_names, args.proxy_list.split(',')
    if args.proxy_list != '':
        proxies = args.proxy_list.split(',')
    else:
        proxies = []
    print proxies
    print args.name
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

def getSQSConn():
  
  try:
    conn = boto.sqs.connect_to_region(AWS_REGION)
    if conn == None:
      sys.stderr.write("Could not connect to AWS region '{0}'\n".format(AWS_REGION))
      sys.exit(1)
    my_q = conn.create_queue("queue_name")

  except Exception as e:
    sys.stderr.write("Exception connecting to SQS\n")
    sys.stderr.write(str(e))
    sys.exit(1)

  return my_q

def getTable(table_name):
  try: 
      DB_table = Table.create(table_name, schema=[HashKey('id')], connection = boto.dynamodb2.connect_to_region(AWS_REGION))
  
  except boto.exception.JSONResponseError as table_warning:
      if table_warning.body['message'] == "Table already exists: " + args.name:
        DB_table = Table(table_name, connection = boto.dynamodb2.connect_to_region(AWS_REGION))
      else:
        raise table_warning
      
  except Exception as e:
      sys.stderr.write("Exception connecting to DynamoDB\n")
      sys.stderr.write(str(e))
      sys.exit(1)

  return DB_table


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
    global dbname_a

 
 
    parser = build_parser()
    args = parser.parse_args()
   
    dbname_a = args.name_all.split(',')

    print dbname_a
    for x in range (0,1):
   		print dbname_a[x]
    
    '''
  for num in range(1,3):
    parser = build_parser()
    args = parser.parse_args()
    okay = args.name
    print okay
    yaya = args.proxy_list
    print yaya
      print "lalal"
  	'''

    #connect to sqs queues
    in_sqs = getSQSConn()
    out_sqs = getSQSConn()
   
    
    # Set up the Database
    db_table = getTable(args.name)

   
    #Initialize request id from durable storage
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
    with kzcl(kazooclientlast.KazooClientLast(hosts=args.zkhost)) as kz, \
        zmqcm(zmq.Context.instance()) as zmq_context:

        # Set up publish and subscribe sockets
        setup_pub_sub(zmq_context, args.sub_to_name)

        # Initialize sequence numbering by ZooKeeper
        try:
            kz.create(path=SEQUENCE_OBJECT, value="0", makepath=True)
        except kazoo.exceptions.NodeExistsError as nee:
            kz.set(SEQUENCE_OBJECT, "0") # Another instance has already created the node
                                         # or it is left over from prior runs

        # Wait for all DBs to be ready
        barrier_path = APP_DIR+BARRIER_NAME
        kz.ensure_path(barrier_path)
        b = kz.create(barrier_path + '/' + args.name, ephemeral=True)
        while len(kz.get_children(barrier_path)) < args.number_dbs:
            time.sleep(1)
        print "Past rendezvous"

        # Now the instances can start responding to requests

        seq_num = kz.Counter(SEQUENCE_OBJECT)

        input_q=getSQSConn()
        while True:
          print "lalala"

          req_smg = input_q.read()
          datajson = pub_socket.recv()
          
          seqid = datajson["seq"]
          seqdata = datajson["data"]
          if datajson:
            if seqid == seq_num.last_set:
              #DO SOME OPERATIONS
            else:
              h = heap.sqsheapq(seqid)
              h.create(seqid, seqdata)
          if not req_smg:
            time.sleep(5)
          else:
            for soc in sub_sockets
              senddata(soc, seq_num.last_set, req_smg)
          	seq_num+=1
          	
            #time.sleep(1)

def send(socket, seq, data):
  ''' Send data through provided socket. '''
  senddata = {"seq": seq, "data": data}
  socket.send_json(senddata)
# Standard Python shmyntax for the main file in an application
if __name__ == "__main__":
    main()
