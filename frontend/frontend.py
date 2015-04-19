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
from boto.dynamodb2.items import Item
from boto.dynamodb2.fields import HashKey, RangeKey, KeysOnlyIndex, GlobalAllIndex
from boto.dynamodb2.table import Table
from boto.exception import JSONResponseError
from bottle import route, run, request, response, abort, default_app, HTTPResponse



DEFAULT_INPUT_Q_NAME = "inQueue"
AWS_REGION = "us-west-2"
WEB_PORT = 8080



def build_parser():
	''' Define parser for command-line arguments '''
	parser = argparse.ArgumentParser(description="Web server demonstrating final project technologies")
	parser.add_argument("name", help="Name of Queue", nargs='?', default=DEFAULT_INPUT_Q_NAME)
	parser.add_argument("web_port", type=int, help="Web server port number", nargs='?', default=WEB_PORT)
	#args = parser.parse_args()
#	print args.name
	return parser
#	argument1 =sys.argv[1]
	#print argument1

def main():
	#argument1 =sys.argv[1]
	#print argument1
	global web_port
	global queuename
	global in_Q_conn

	parser = build_parser()
	args = parser.parse_args()
	queuename = args.name
	web_port  = args.web_port

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

	import frontoperations
	#my_sqs = getConn()
	#return operations.do_delete(my_sqs)

	return frontoperations.do_delete(in_Q_conn)

@route('/create')
def create():
	global in_Q_conn

	import frontoperations
	#my_sqs = getConn()
	#return operations.do_create(my_sqs)

	return frontoperations.do_create(in_Q_conn)

@route('/add_activities')
def add_activities():
	global in_Q_conn
	import frontoperations
	#my_sqs = getConn()
	#return operations.do_add_activities(my_sqs)
	return frontoperations.do_add_activities(in_Q_conn)

@route('/retrieve')
def retrieve():
	global in_Q_conn
	import frontoperations
	#my_sqs = getConn()
	#return operations.do_retrieve(my_sqs)
	return frontoperations.do_retrieve(in_Q_conn)


# Standard Python shmyntax for the main file in an application

if __name__ == "__main__":
    main()
    

