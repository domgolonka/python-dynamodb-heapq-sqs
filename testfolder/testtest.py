#!/usr/bin/env python

"""Test CounterLast"""

import sys
import time
import argparse

import kazooclientlast

import kazoo.exceptions

ZK_HOST = "cloudsmall1.cs.surrey.sfu.ca"
APP_DIR = "/TEST"
BARRIER_NAME = "/Ready"
SEQ_NODE = APP_DIR + "/Hoo"

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Test CounterLast")
    parser.add_argument("n", type=int, help="Number of trials")
    parser.add_argument("name", help="Name of file in which to write results")
    parser.add_argument("number_instances", type=int, help="Number of test instances")
    parser.add_argument("seq", help="Name of node to use as sequence", nargs='?', default=SEQ_NODE)
    parser.add_argument("zkhost", help="Name of ZooKeeper host", nargs='?', default=ZK_HOST)
    args = parser.parse_args()

    kz = kazooclientlast.KazooClientLast(args.zkhost)
    kz.start()

    # Initialize sequence numbering by ZooKeeper
    try:
        kz.create(path=args.seq, value="0", makepath=True)
    except kazoo.exceptions.NodeExistsError as nee:
        kz.set(args.seq, "0") # Another instance has already created the node
                              # or it is left over from prior runs

    # Wait for all instances to be ready
    barrier_path = APP_DIR+BARRIER_NAME
    kz.ensure_path(barrier_path)
    b = kz.create(barrier_path + '/' + args.name, ephemeral=True)
    while len(kz.get_children(barrier_path)) < args.number_instances:
        time.sleep(1)
    print "Past start rendezvous"

    s = kz.Counter(args.seq)

    results = [-1] * args.n
    
    for i in xrange(args.n):
        s += 1
        results[i] = s.last_set

    with open(args.name, 'w') as out:
        for val in results:
            out.write('{0}\n'.format(val))

    # Wait for all instances to complete
    while s.value < args.n * args.number_instances:
        time.sleep(1)
    print "Past end rendezvous"

    kz.stop()
    kz.close()