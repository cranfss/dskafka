import json
import subprocess
import time
from confluent_kafka import Producer
from confluent_kafka import Consumer, KafkaError

 

#get list of external dns nodes in json
nodejson = json.loads(subprocess.check_output(['kubectl', 'get', 'nodes', '-o', 'json']))

nodelist = [] 

def getextnodenames():
	for node in nodejson["items"]:
		if node["metadata"]["labels"]["kubernetes.io/role"] == "master":
			continue
		else:
			for item in node["status"]["addresses"]:
				if item["type"] == "ExternalDNS":
					nodelist.append(item["address"])
	print ('Found %d nodes' % len(nodelist))
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
#kafkacat -b ec2-54-153-75-2.us-west-1.compute.amazonaws.com:31090 -t ext-test-topic
#kafkacat -C -b  ec2-54-153-75-2.us-west-1.compute.amazonaws.com:31090 -t ext-test-topic

#produce to first nodeport
p = Producer({'bootstrap.servers': producingnode})
p.produce(topicname, key='hello', value='world')
p.flush(30)


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
        break
    elif msg.error().code() == KafkaError._PARTITION_EOF:
        print('End of partition reached {0}/{1}'
              .format(msg.topic(), msg.partition()))
        break
    else:
        print('Error occured: {0}'.format(msg.error().str()))
        break

c.close()


#print ('Found %d nodes [%s]' % len(nodelist), ', '.join(map(str, nodelist)))