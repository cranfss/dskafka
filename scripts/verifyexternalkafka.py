#!/usr/bin/python

import json
import subprocess
import time
import argparse
from confluent_kafka import Producer
from confluent_kafka import Consumer, KafkaError

parser = argparse.ArgumentParser()
parser.add_argument("-n", "--numnodes", type=int, required=True, help="Number of worker nodes")
args = parser.parse_args()
print "numnodes={}".format(args.numnodes)

#get list of external dns nodes in json
nodejson = json.loads(subprocess.check_output(['kubectl', 'get', 'nodes', '-o', 'json']))

nodelist = [] 

#parse json to get external dns hostnames
def getextnodenames():
	for node in nodejson["items"]:
		if node["metadata"]["labels"]["kubernetes.io/role"] == "master":
			continue
		else:
			for item in node["status"]["addresses"]:
				if item["type"] == "ExternalDNS":
					nodelist.append(item["address"])
	print ('Expected %d nodes, found %d nodes' % (args.numnodes, len(nodelist)))
	for items in nodelist:
		print(items)	
	return nodelist

#get list of external dns nodes
nodes = getextnodenames()

#list of externally exposed ports
nodeport = ["31090", "31091"]

topicname = "ext-test-topic"

#seed test message
testmsg = time.time()
producingnode = str(nodes[0]) + ":" + str(nodeport[0])
consumingnode = str(nodes[1]) + ":" + str(nodeport[1])

#produce to first nodeport
p = Producer({'bootstrap.servers': producingnode})
p.produce(topicname, str(testmsg))
p.flush(30)
print('Sent message: %s' % testmsg)

#give consumer a few seconds
time.sleep(2) 

#consume from second nodeport
settings = {
    'bootstrap.servers': consumingnode,
    'group.id': 'mygroup',
    'client.id': 'client-1',
    'enable.auto.commit': True,
    'session.timeout.ms': 6000,
    'default.topic.config': {'auto.offset.reset': 'smallest'}
}

c = Consumer(settings)
c.subscribe([topicname])

while True:
    msg = c.poll(0.1)
    if msg is None:
        continue
    elif not msg.error():
        print('Received message: {0}'.format(msg.value()))
        if msg.value()==str(testmsg):
        	print "success"
        	c.close()
        	exit(0)
        else:
        	print "messages did not match"
        	exit(1)
    elif msg.error().code() == KafkaError._PARTITION_EOF:
        print('End of partition reached {0}/{1}'
              .format(msg.topic(), msg.partition()))
        c.close()
        exit(1)
    else:
        print('Error occured: {0}'.format(msg.error().str()))
        c.close()
        exit(1)
