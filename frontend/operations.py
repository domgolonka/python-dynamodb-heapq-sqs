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



DEL_QUERY_PATTERN = "^id=[0-9]|^name=[a-zA-Z_ ]"
ADD_ACTS_QUERY_PATTERN = "id=[0-9]+&activities=[a-zA-Z_ ]+[,a-zA-Z_ ]+"

del_pat = re.compile(DEL_QUERY_PATTERN)
addActs_pat = re.compile (ADD_ACTS_QUERY_PATTERN)

AWS_REGION = "us-west-2"
PORT = 8080

def do_delete(my_sqs):
	msg = ""
	msg_status = 404 #assume is an error to start of with
	
	if not del_pat.match(request.query_string):
		print"delete has been called\n"
		abort(404, "Query string does not match pattern '{0}'".format(DEL_QUERY_PATTERN))

	if "id" in request.query: #checks to see if the request is by id
		id_delete = request.query_string + '&'#adding in a end marker
		begin = id_delete.index("id=") + len("id=")
		end = id_delete.index("&",begin) # find the end index
		id_delete = id_delete[begin:end]
		sqs_msg = { "req_type": "delete", "data": { "type": "person", "id" : str(id_delete) } }
		msg = {"data":"Query sent to SQS"}
		msg_status = 200
		

	elif "name" in request.query: #checks to see if delete request if by name
		get_name = request.query.name
		sqs_msg = { "req_type": "delete", "data": { "type": "person", "name" : get_name} }
		msg = {"data":"Query sent to SQS"}
		msg_status = 200

	f = boto.sqs.message.Message()
	f.set_body(json.dumps(sqs_msg))
	my_sqs.write(f)
	return HTTPResponse(status=msg_status, body=json.dumps(msg,indent=4))

def do_add_activities(my_sqs):
	#msg = ""
	#msg_status = 404

	print"Add_Activities has been called\n"
	if not addActs_pat.match(request.query_string):
            abort(404, "Query string does not match pattern '{0}'".format(ADD_ACTS_QUERY_PATTERN))
 	
   	#id_query = parse_input(request.query_string+'&',"id=")
   	id_addAct = request.query.id
   	activities = request.query_string+'&'
   	begin = activities.index("activities=") + len("activities=")
   	end = activities.index("&", begin)
   	activities_list = activities[begin:end]

   	sqs_msg = { "req_type" : "add_activities", 'data': {"type":"person", "id": id_addAct, "activities": activities_list}}
   	msg = { "data": {"type": "Notification", "msg": "Accepted"} }

   	f = boto.sqs.message.Message()
   	f.set_body(json.dumps(sqs_msg))
   	my_sqs.write(f)

	return HTTPResponse(status=200, body=json.dumps(msg, indent=4))