#!/usr/bin/env python

'''
  CMPT 474-V0.5 ASSIGNMENT 3-BASICDB
'''

# Library packages
from boto.sqs.message import RawMessage
import os
import re
import os, time
import sys
import json
import boto.sqs
import boto.sqs.message
import boto.dynamodb2
import json

from boto.dynamodb2.items import Item
from boto.dynamodb2.fields import HashKey, RangeKey, KeysOnlyIndex, GlobalAllIndex
from boto.dynamodb2.table import Table
from boto.exception import JSONResponseError
from bottle import route, run, request, response, abort, default_app, HTTPResponse

def db_main():
	AWS_REGION = AWS_REGION = "us-west-2"
	try:
	    conn = boto.sqs.connect_to_region(AWS_REGION)
	    if conn == None:
	        sys.stderr.write("Could not connect to AWS region '{0}'\n".format(AWS_REGION))
	        sys.exit(1)


	    input_q = conn.get_queue("sqs_in_queue")
	    #input_q.set_message_class()
	    

	except Exception as e:
	    sys.stderr.write("Exception connecting to SQS\n")
	    sys.stderr.write(str(e))
	    sys.exit(1)

	try: #output quque 
	    conn = boto.sqs.connect_to_region(AWS_REGION)
	    if conn == None:
	        sys.stderr.write("Could not connect to AWS region '{0}'\n".format(AWS_REGION))
	        sys.exit(1)


	    output_q = conn.create_queue("sqs_out_queue")
	    #input_q.set_message_class()
	    

	except Exception as e:
	    sys.stderr.write("Exception connecting to SQS\n")
	    sys.stderr.write(str(e))
	    sys.exit(1)





	try: 
			DB1_table = Table.create('DB1_table', schema=[HashKey('id')], connection = boto.dynamodb2.connect_to_region(AWS_REGION))
	except boto.exception.JSONResponseError	as table_warning:
			if table_warning.body['message'] == "Table already exists: DB1_table":
				DB1_table = Table('DB1_table',connection = boto.dynamodb2.connect_to_region(AWS_REGION))
			else:
				raise table_warning
			
	except Exception as e:
			sys.stderr.write("Exception connecting to DynamoDB\n")
			sys.stderr.write(str(e))
			sys.exit(1)




	while True:
		print "lalala"

		req_smg = input_q.read()
		
		
		if not req_smg:
			time.sleep(1)
		else:
			req = json.loads(req_smg.get_body())
			if req["req_type"] =="delete":
				print "Im deleting"
			#	time.sleep(4)
				import DBoperations
				msg = DBoperations.do_delete(req,DB1_table,output_q)
				
			elif req["req_type"]=="retrieve":
				print "Im retrieving"
				import DBoperations
				msg = DBoperations.do_retrieve(req,DB1_table,output_q)
			
			
			

			







	    
