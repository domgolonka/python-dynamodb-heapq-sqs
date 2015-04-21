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
def do_operation(req_smg,DB1_table,output_q,boolprime):
	req =req_smg
	req = json.loads(req_smg)


	if req["req_type"] =="delete":
		print "Im deleting"
		do_delete(req,DB1_table,output_q,boolprime)
	elif req["req_type"]=="retrieve":
		print "Im retrieving"
		do_retrieve(req,DB1_table,output_q,boolprime)
	elif req["req_type"] == "create":
		print "Im creating"
		do_create(req,DB1_table,output_q,boolprime)
	elif req["req_type"]=="add_activities":
		print "Im addig activities"
		do_add_activities(req,DB1_table,output_q,boolprime)

def do_delete(req,DB1_table,output_q,boolprime):
	msg = ""
	msg_status = 404 #assume is an error to start of with
	msg_q =""
	id_delete=""
	if req["by"]=="id":
		
		id_delete = req["data"]["id"]
		print id_delete
		try:
			delete_item= DB1_table.get_item(id=id_delete)
			delete_item.delete()
			msg_q= { "data": { "type": "person", "id" : str(id_delete) } }
			msg_status = 200
		except Exception as id_doesnt_exist:
			msg_q= {"errors":[{"not_found":{"id": str(id_delete)}}]}
			msg_status = 404

	elif req["by"]=="name":
		get_name = req["data"]["name"]
		try:
		 	query=DB1_table.scan()
		 	for res in query:
				if req['name'] == get_name:  #if the name matahes it breaks out
					delete_id = res['id']
					break
			delete_item2= DB1_table.get_item(id=delete_id)
			
			delete_item2.delete()
			msg_q = { "data": { "type": "person", "id" : str(delete_id) } }
			msg_status = 200

		except Exception as id_doesnt_exist:
			print "i get to error"
			msg= {"errors":[{"not_found":{"name": str(get_name)}}]}
			msg_status = 404

	out_msg = boto.sqs.message.Message()
	out_msg.set_body(json.dumps(msg_q,indent=4))
	output_q.write(out_msg)


	return 1 #do we really need to turn anything ?

def do_retrieve(req,DB1_table,output_q,boolprime):
	msg = ""
	msg_status = 404 #assume is an error to start of with
	msg_q =""
	id_delete=""
	if req["by"]=="id":
		id_retrieve = req ["data"]["id"]
		print id_retrieve
		try:
			retrieve_item = DB1_table.get_item(id = id_retrieve)
			msg_q= {"data": {"type" : "person", "id": str(id_retrieve)}}
			msg_status = 200
		except Exception as id_doesnt_exist:
			msg_q= {"errors":[{"not_found":{"id": str(id_retrieve)}}]}
			msg_status = 404
			
	elif req["by"]=="name":
		get_name = req["data"]["name"]
		try:
		 	query=DB1_table.scan()
		 	for res in query:
				if res['name'] == get_name:  #if the name matahes it breaks out
					retrieve_id = res['id']
					break
			delete_item2= DB1_table.get_item(id=retrieve_id)
			msg_q = { "data": { "type": "person", "id" : str(retrieve_id) } }
			msg_status = 200

		except Exception as name_doesnt_exist:
			msg_q= {"errors":[{"not_found":{"name": str(get_name)}}]}
			msg_status = 404
	out_msg = boto.sqs.message.Message()
	out_msg.set_body(json.dumps(msg_q, indent=4))
	output_q.write(out_msg)

def do_add_activities(req,DB1_table,output_q,boolprime):
	try:
		activity_id = req["data"]["id"]
		activity_query = req["data"]["activities"]
		activity_list= activity_query.split(',')
		print activity_list
		user = DB1_table.get_item(id=activity_id)
		existing_activities = user['activities']
		#list_new_activities = activity_query	#list of activities from the add_activities call
		added_activities = [] #activities actually added
		for new_act in activity_query:
			if (existing_activities.count(new_act) == 0):
				existing_activities = new_act +activity_query
				user['activities'] = existing_activities
				print "users"
				print user['activities']
				user.save()
		msg_q= {'data': {'type':'person', 'id': activity_id, 'activities': added_activities}}
		out_msg = boto.sqs.message.Message()
		out_msg.set_body(json.dumps(msg_q,indent=4))
		output_q.write(out_msg)
	except Exception as name_doesnt_exist:
			msg_q= {"errors":[{"not_found":{"id": str(activity_id)}}]}
			msg_status = 404
	out_msg = boto.sqs.message.Message()
	out_msg.set_body(json.dumps(msg_q, indent=4))
	output_q.write(out_msg)
def do_create(req,DB1_table,output_q,boolprime):
	id_query = req["data"]["id"]
	name_query = req["data"]["name"]
	activities_query = req["data"]["activities"]
	try:
		DB1_table.put_item(data = {
										'type':'person',
										'id':str(id_query), 
										'name':str(name_query), 
										'activities':activities_query
										})
		msg_status = 201
		msg_q= {'data':{'type':'person', 'id': id_query}}#, "links":{"self":"http://localhost:8080/retrieve?id="+ str(id_query)}}}
	except Exception as acctivities_or_name_differ:
		check_item = DB1_table.get_item(id = str(id_query))
		print "soemthing from the check_item"
		print check_item['name']
		print check_item['activities']
		check_name = str(check_item['name'])
		if check_name == name_query:# check if the input name is differ than the existing item name
			print " i got to json"
			list_activities = check_item['activities']#list of existing activities
			print "after jason"
			list_new_activities= req["data"]["activities"]# list of input activitis
			for list in list_new_activities: # check if the input activities are differ than the item activities in the DB
				if list not in list_activities:
					msg_status= 400
					msg_q= {'error':[{
							'id_exists':{
								'status': msg_status,
								'title':'id already exists', 
								'detail': {
									'name':name_query, 
									'activities':activities_query}
									}
									}]
									}
					out_msg = boto.sqs.message.Message()
					out_msg.set_body(json.dumps(msg_q, indent =4))
					return output_q.write(out_msg)
		else:
				msg_status= 400
				msg_q = {'error':[{
						'id_exists':{
							'status': msg_status,
							'title':'id already exists', 
							'detail': {
								'name':name_query, 
								'activities':activities_query}
								}
								}]
								}
				out_msg = boto.sqs.message.Message()
				out_msg.set_body(json.dumps(msg_q,indent=4))
				output_q.write(out_msg)
def parse_input(input_string, attr):# this function parse the input and return the attribute values
	try:
		
		begin = input_string.index(attr) + len(attr)# find the start of the value for the given attribute
		end = input_string.index("&", begin)# find the end of the value for the given attribute
		return input_string[begin:end]# return the trimed value of the attribute. everything between the attr= and the firts'&''
	except ValueError:
		return ""


		



	
