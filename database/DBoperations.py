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

def do_delete(req,DB1_table,output_q):
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
			msg = { "data": { "type": "person", "id" : str(id_delete) } }
			msg_status = 200
		except Exception as id_doesnt_exist:
			msg_q= {"errors":[{"not_found":{"id": str(id_delete)}}]}
			msg_status = 404

	elif req["by"]=="name":
		get_name = req["data"]["name"]
		try:
		 	query=DB1_table.scan()
		 	for res in query:
				if res['name'] == get_name:  #if the name matahes it breaks out
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
	out_msg.set_body(json.dumps(msg_q))
	output_q.write(out_msg)


	return 1 #do we really need to turn anything ?



	
