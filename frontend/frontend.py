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
PORT = 8080



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



app = default_app()
run(app, host="localhost", port=PORT)


    
