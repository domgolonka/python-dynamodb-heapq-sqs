#!/usr/bin/env python
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

AWS_REGION = "us-west-2"
WEB_PORT = 8081
DEFAULT_OUT_Q = "outQ"

def build_parser():
    ''' Define parser for command-line arguments '''
    parser = argparse.ArgumentParser(description="Web server demonstrating final project technologies")
    parser.add_argument("name", help="Name of Queue", nargs='?', default=DEFAULT_OUT_Q)
    parser.add_argument("web_port", type=int, help="Web server port number", nargs='?', default=WEB_PORT)
    return parser

@route('/')
def app():
	global out_Q_conn
	m = out_Q_conn.read()

	if not m:
		response.status = 204
		return ''
	else:
		response.status = 201
		response_msg = m.get_body()
		out_Q_conn.delete_message(m)
		return response_msg

def main():
	global out_Q_conn

	parser = build_parser()
	args = parser.parse_args()
	out_Q_conn = getConn(args.name)

	print "-- BACKEND --"
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

# Standard Python shmyntax for the main file in an application
if __name__ == "__main__":
    main()

