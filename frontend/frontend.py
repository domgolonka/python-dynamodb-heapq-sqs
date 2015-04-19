#!/usr/bin/env python

'''
  CMPT 474-V0.5 ASSIGNMENT 3-BASICDB
'''

# Library packages
import os
import re
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

import zmq
import kazoo.exceptions
import kazooclientlast


import gen_ports
import DB

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
#DEFAULT_NAME = INPUT_QUEUE
BARRIER_NAME = "/Ready"


DEFAULT_INPUT_Q_NAME = "inQueue"
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
    parser.add_argument("web_port", type=int, help="Web server port number", nargs='?', default=WEB_PORT)
    parser.add_argument("name", help="Name of Queue", nargs='?', default=DEFAULT_INPUT_Q_NAME)
    return parser



def main():
	global queuename
	global in_Q_conn

	parser = build_parser()
	args = parser.parse_args()
	queuename = args.name

	in_Q_conn = getConn()

	app = default_app()
	run(app, host="localhost", port=args.web_port)

def getConn():
	global queuename
	try:
		conn = boto.sqs.connect_to_region(AWS_REGION)
		if conn == None:
			sys.stderr.write("Could not connect to AWS region '{0}'\n".format(AWS_REGION))
			sys.exit(1)

		my_q = conn.create_queue(queuename)

	except Exception as e:
		sys.stderr.write("Exception connecting to SQS\n")
		sys.stderr.write(str(e))
		sys.exit(1)

	return my_q



@route('/delete')
def delete():
	global in_Q_conn

	import operations
	#my_sqs = getConn()
	#return operations.do_delete(my_sqs)

	return operations.do_delete(in_Q_conn)

@route('/create')
def create():
	global in_Q_conn

	import operations
	#my_sqs = getConn()
	#return operations.do_create(my_sqs)

	return operations.do_create(in_Q_conn)

@route('/add_activities')
def add_activities():
	global in_Q_conn
	import operations
	#my_sqs = getConn()
	#return operations.do_add_activities(my_sqs)
	return operations.do_add_activities(in_Q_conn)

@route('/retrieve')
def retrieve():
	global in_Q_conn
	import operations
	#my_sqs = getConn()
	#return operations.do_retrieve(my_sqs)
	return operations.do_add_retrieve(in_Q_conn)


# Standard Python shmyntax for the main file in an application
if __name__ == "__main__":
    main()
    

