import kazoo.client
import contextlib
import time

import pprint

import logging
logging.basicConfig()


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
        #kz.stop()
        #kz.close()


def toink(kz):
  #our group name
  #APP_DIR = "/group-tooMuchCoffee"
  APP_DIR = "/test"
  #setting up seq object
  SEQUENCE_OBJECT = APP_DIR + "/SeqNum"

  # Initialize sequence numbering by ZooKeeper  
  if not kz.exists(SEQUENCE_OBJECT):
      kz.create(SEQUENCE_OBJECT, "0")
  else:
      kz.set(SEQUENCE_OBJECT, "0")
  
  
  BARRIER_NAME = "/Ready"

  #wait for all DBs to be ready
  barrier_path = APP_DIR + BARRIER_NAME

  kz.ensure_path(barrier_path)
  #tmp - to be from paramaeter arg
  front_end_name = "DB1"
  num_dbs = 1

  b = kz.create(barrier_path + '/' + front_end_name, ephemeral=True)

  while len(kz.get_children(barrier_path)) < num_dbs:
      time.sleep(1)
  print "Past rendezvous"

  seq_num = kz.Counter(SEQUENCE_OBJECT)
  print seq_num.value
  #when you need a fresh, unique counter value
  seq_num += 1
  v = seq_num.value #the value is in the .last_seq field
  print v 

  children = kz.get_children(barrier_path)
  print children
  print children[0]

  kz.set(barrier_path+'/DB1', "testingdata,123") #data has to be a byte string

  data, stat = kz.get(barrier_path+"/"+children[0])
  print "data:"+data
  if data == "":
    print "data empty"
  print stat

  y = data.split(",")
  print y[0]
  print y[1]



with kzcl(kazoo.client.KazooClient(hosts='cloudsmall1.cs.surrey.sfu.ca')) as kz:
  
  toink(kz)

print "--------------------"
print "wassup bro"
print "--------------------"





