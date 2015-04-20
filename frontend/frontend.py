#!/usr/bin/env python

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

DEFAULT_INPUT_Q_NAME = "inQ"
AWS_REGION = "us-west-2"
WEB_PORT = 8080

def build_parser():
	''' Define parser for command-line arguments '''
	parser = argparse.ArgumentParser(description="Web server demonstrating final project technologies")
	parser.add_argument("name", help="Name of Queue", nargs='?', default=DEFAULT_INPUT_Q_NAME)
	parser.add_argument("web_port", type=int, help="Web server port number", nargs='?', default=WEB_PORT)

	return parser


def main():
	global in_Q_conn

	parser = build_parser()
	args = parser.parse_args()

	in_Q_conn = getConn(args.name)

	print "-- FRONTEND --"
	app = default_app()
	run(app, host="localhost", port=args.web_port)

def getConn(queue_name):
	try:
		conn = boto.sqs.connect_to_region(AWS_REGION)
		if conn == None:
			sys.stderr.write("Could not connect to AWS region '{0}'\n".format(AWS_REGION))
			sys.exit(1)

		my_q = conn.create_queue(queue_name)

	except Exception as e:
		sys.stderr.write("Exception connecting to SQS\n")
		sys.stderr.write(str(e))
		sys.exit(1)

	return my_q

@route('/delete')
def delete():
	global in_Q_conn
	import frontoperations
	return frontoperations.do_delete(in_Q_conn)

@route('/create')
def create():
	global in_Q_conn

	import frontoperations
	return frontoperations.do_create(in_Q_conn)

@route('/add_activities')
def add_activities():
	global in_Q_conn
	import frontoperations
	return frontoperations.do_add_activities(in_Q_conn)

@route('/retrieve')
def retrieve():
	global in_Q_conn
	import frontoperations
	return frontoperations.do_retrieve(in_Q_conn)

# Standard Python shmyntax for the main file in an application
if __name__ == "__main__":
    main()
    

