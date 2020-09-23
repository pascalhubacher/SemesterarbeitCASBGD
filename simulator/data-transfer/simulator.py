#
import time
from datetime import datetime, timedelta
import math
import os
import itertools
import json
import re
import sys
from multiprocessing import Pool
from confluent_kafka import Producer, Consumer, admin
#Admin -> get/create/delete topics
from confluent_kafka.admin import AdminClient, NewTopic
#AVRO
from confluent_kafka import avro
#from confluent_kafka.avro import SchemaRegistryClient, Schema
#AVRO Producer
from confluent_kafka.avro import AvroProducer
#AVRO Consumer
from confluent_kafka.avro import AvroConsumer
from confluent_kafka.avro.serializer import SerializerError


# Globals
# JSON keys
STR_PATH = 'path'
STR_MATCH_ID = 'TracabMetaData.match.iId'
STR_MATCH_DATE = 'TracabMetaData.match.dtDate'
STR_MATCH_TIME = 'TracabMetaData.match.dtTime'
STR_MATCH_FRAMERATE = 'TracabMetaData.match.iFrameRateFps'
STR_PITCH_X = 'TracabMetaData.match.fPitchXSizeMeters'
STR_PITCH_Y = 'TracabMetaData.match.fPitchYSizeMeters'
STR_CONFIG_PROPERTIES = 'config.properties'
STR_NUMBER_OF_ELEMENTS = 'number_of_elements'
STR_WORK = 'work'
LST_NOT_ELEMENT = [STR_NUMBER_OF_ELEMENTS]
STR_HOME = 'home'
STR_AWAY = 'away'
STR_BALL = 'ball'
STR_OTHER = 'other'
#time laps
INT_TIME_LAPS = 1

#list of all kafka brokers
#kafka_brokers = ['kafka-1:9092', 'kafka-2:9093', 'kafka-3:9094']
kafka_brokers = ['kafka-1:9092']
kafka_topics = ['rawGames', 'fbBallPossession', 'rawMetaMatch']

#create kafka topics
def kafka_topics_create(broker_list, topic_list):
    for kafka_srv_elem in broker_list:
        kafka_servers_str += ', ' + kafka_srv_elem
    
    a = AdminClient({
        'bootstrap.servers': kafka_servers_str
    })

    #new_topics = [NewTopic(topic, num_partitions=30, replication_factor=3) for topic in topic_list]
    new_topics = [NewTopic(topic, num_partitions=int(len(broker_list)), replication_factor=int(len(broker_list))) for topic in topic_list]
    # Note: In a multi-cluster production scenario, it is more typical to use a replication_factor of 3 for durability.

    # Call create_topics to asynchronously create topics. A dict
    # of <topic,future> is returned.
    fs = a.create_topics(new_topics)

    # Wait for each operation to finish.
    for topic, f in fs.items():
        try:
            f.result()  # The result itself is None
            print("Topic {} created".format(topic))
        except Exception as e:
            print("Failed to create topic {}: {}".format(topic, e))
    
#list kafka topics
def kafka_topics_get(broker_list):
    kafka_servers_str = ''
    for kafka_srv_elem in broker_list:
        kafka_servers_str += ', ' + kafka_srv_elem
        
    kadmin = AdminClient({
        'bootstrap.servers': kafka_servers_str
    })

    #Returns a dict(). See example below.
    #{'topic01': TopicMetadata(topic01, 3 partitions),}
    return(kadmin.list_topics().topics)
    
#Consumer - read messages from kafka
def kafka_consumer(broker_list, message, topic, group_id = 'mygroup'):
    kafka_servers_str = ''
    for kafka_srv_elem in broker_list:
        kafka_servers_str += ', ' + kafka_srv_elem

    c = Consumer({
        'bootstrap.servers': kafka_servers_str,
        'group.id': group_id,
        'auto.offset.reset': 'earliest'
    })

    c.subscribe([topic])

    while True:
        msg = c.poll(1.0)

        if msg is None:
            continue
        if msg.error():
            print("Consumer error: {}".format(msg.error()))
            continue

        print('Received message: {}'.format(msg.value().decode('utf-8')))

    c.close()

# not used as the producer have to be created only once per data file and not for each message -> errors
#Producer - write messages to kafka
def kafka_producer(broker_list, message, topic, key = '1'):
    #############################
    # confluent kafka Producer
    #############################

    kafka_servers_str = ''
    for kafka_srv_elem in broker_list:
        kafka_servers_str += ', ' + kafka_srv_elem

    p = Producer({'bootstrap.servers': kafka_servers_str})

    def delivery_report(err, msg):
        """ Called once for each message produced to indicate delivery result.
            Triggered by poll() or flush(). """
        if err is not None:
            print('Message delivery failed: {}'.format(err))
        else:
            #print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))
            pass

    # Asynchronously produce a message, the delivery report callback
    # will be triggered from poll() above, or flush() below, when the message has
    # been successfully delivered or failed permanently.
    
    # Trigger any available delivery report callbacks from previous produce() calls
    p.poll(0)

    # No Key
    #p.produce(topic, data.encode('utf-8'), callback=delivery_report)
    
    # with key
    p.produce(str(topic), key=str(key), value = message.encode('utf-8'), callback=delivery_report)

    # Wait for any outstanding messages to be delivered and delivery report
    # callbacks to be triggered.
    p.flush()

#register schema in schema registry
def schema_registry_register(ip='schema-registry-1', port=8081):
    schema_str = """
        {
            "type": "record",
            "name": "data",
            "fields": [
                {"name": "ts", "type": "int"},
                {"name": "x",  "type": "double"}
                {"name": "y",  "type": "double"}
                {"name": "z",  "type": "double"}
                {"name": "id",  "type": "string"}
            ]
        }
    """

    #avro_schema = Schema(schema_str, 'AVRO')
    #sr = SchemaRegistryClient("http://"+ip+":"+port)    
    #_schema_id = client.register_schema("basicavro", avro_schema)
    #return(_schema_id)

#AVRO Consumer - read messages from kafka (schema registry needed)

#AVRO Producer - write messages to kafka (schema registry needed)
def kafka_producer_avro(ip, port, value, topic, key='1', schema_registry='http://localhost:8081'):
    value_schema_str = """
    {
    "namespace": "my.test",
    "name": "value",
    "type": "record",
    "fields" : [
        {
        "name" : "name",
        "type" : "string"
        }
    ]
    }
    """

    key_schema_str = """
    {
    "namespace": "my.test",
    "name": "key",
    "type": "record",
    "fields" : [
        {
        "name" : "name",
        "type" : "string"
        }
    ]
    }
    """

    value_schema = avro.loads(value_schema_str)
    key_schema = avro.loads(key_schema_str)
    value = {"name": "Value"}
    key = {"name": "Key"}


    def delivery_report(err, msg):
        """ Called once for each message produced to indicate delivery result.
            Triggered by poll() or flush(). """
        if err is not None:
            print('Message delivery failed: {}'.format(err))
        else:
            print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))


    avroProducer = AvroProducer({
        'bootstrap.servers': ip+':'+port,
        'on_delivery': delivery_report,
        'schema.registry.url': schema_registry
        }, default_key_schema=key_schema, default_value_schema=value_schema)

    avroProducer.produce(topic=topic, value=value, key=key)
    avroProducer.flush()

#read data file and execute line by line waiting in between and write to kafka
def execute_log_data(param_list):
    #get last element (dct_data[STR_CONFIG_PROPERTIES]) and remove it from list
    kafka_broker_list = param_list.pop()
    
    #get last element (dct_data[STR_CONFIG_PROPERTIES]) and remove it from list
    config_properties = param_list.pop()
   
    #get last element (topic) and remove it from list
    topic = param_list.pop()

    #prepare kafka producer
    kafka_servers_str = ''
    for kafka_srv_elem in kafka_broker_list:
        kafka_servers_str += ', ' + kafka_srv_elem
    #print(kafka_servers_str)

    p = Producer({'bootstrap.servers': kafka_servers_str})

    def delivery_report(err, msg):
        """ Called once for each message produced to indicate delivery result.
            Triggered by poll() or flush(). """
        if err is not None:
            print('Message delivery failed: {}'.format(err))
        else:
            #print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))
            pass
    #

    def delivery_report(err, msg):
        """ Called once for each message produced to indicate delivery result.
            Triggered by poll() or flush(). """
        if err is not None:
            print('Message delivery failed: {}'.format(err))
        else:
            #print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))
            pass

    print(' Process player id {} team ({}) started'.format(param_list[0], param_list[1]))
    with open(param_list[2]) as f:
        lines = f.readlines()

    time_elapsed = 0
    i = 0
    for line in lines[1:]: 
        i += 1
        #max 1589645 -> 46min
        if i <= 2000:
            #print(line.strip())
            #40ms -> 40/1000 -> 0.04s
            #the time in the log is cummulated so the last time vales is subtracted each time to get the delta time
            #the time value is divided by the time laps factor which can be set at each run (INT_TIME_LAPS)
            time.sleep((int(line.strip().split(',')[0])- time_elapsed)/1000/INT_TIME_LAPS)
            #the last time value
            time_elapsed = int(line.strip().split(',')[0])

            #"Timestamp","X"  ,"Y" ,"Z","ID"
            #         40,50.92,1.15,0.0,101
            json_event = {}

            #create timestamp of the format ISO 8601 format (YYYY-MM-DDTHH:MM:SS.mmmmmm)
            #Example '2018-06-29 08:15:27.243860'
            date_time_obj = datetime.strptime(config_properties[STR_MATCH_DATE]+'T'+config_properties[STR_MATCH_TIME], '%Y-%m-%dT%H:%M:%S')
            date_time_obj += timedelta(seconds=int(line.strip().split(',')[0])/1000)
            json_event['ts'] = str(date_time_obj.strftime("%Y.%m.%dT%H:%M:%S.%f"))
            #print(json_event['ts'])
            
            json_event['x'] = float(line.strip().split(',')[1])
            json_event['y'] = float(line.strip().split(',')[2])
            json_event['z'] = float(line.strip().split(',')[3])
            json_event['id'] = int(line.strip().split(',')[4])
            json_event['matchid'] = int(config_properties[STR_MATCH_ID])
            #print(line.strip(','), "-:-", json_event)

            #send data to kafka
            #kafka_producer(kafka_broker_list, json.dumps(json_event), topic, key=str(json_event['matchid'])+'.'+str(json_event['id']))
            
            # Trigger any available delivery report callbacks from previous produce() calls
            p.poll(0)
            # with key
            p.produce(str(topic), key=str(json_event['matchid'])+'.'+str(json_event['id']), value = json.dumps(json_event).encode('utf-8'), callback=delivery_report)

        #do something

    # Wait for any outstanding messages to be delivered and delivery report
    # callbacks to be triggered.
    p.flush()

    print(' Process player id {} team ({}) finished'.format(param_list[0], param_list[1])) 

#create json structure out of the data
def create_data_json(filepath):
    #get all filepaths to all files
    dct_data = {}
    number_of_elements = 0
    dct_data[STR_HOME] = {}
    dct_data[STR_AWAY] = {}
    dct_data[STR_BALL] = {}
    dct_data[STR_OTHER] = {}

    # tuple of all the (player_id, home/away/ball, path)
    tpl_work = ()
 
    walker = os.walk(filepath)
    for root, _dirs, files in walker:
       for file_ in files:
            path = os.path.join(root, file_)
            
            if STR_CONFIG_PROPERTIES in path:
                dct_data[STR_CONFIG_PROPERTIES] = {}
                dct_data[STR_CONFIG_PROPERTIES][STR_PATH] = path
                #properties auslesen
                dct_data[STR_CONFIG_PROPERTIES][STR_MATCH_ID] = get_properties(path,STR_MATCH_ID)
                dct_data[STR_CONFIG_PROPERTIES][STR_MATCH_DATE] = get_properties(path,STR_MATCH_DATE)
                dct_data[STR_CONFIG_PROPERTIES][STR_MATCH_TIME] = get_properties(path,STR_MATCH_TIME)
                dct_data[STR_CONFIG_PROPERTIES][STR_PITCH_X] = get_properties(path,STR_PITCH_X)
                dct_data[STR_CONFIG_PROPERTIES][STR_PITCH_Y] = get_properties(path,STR_PITCH_Y)

            elif STR_HOME in path:
                #not the properties file
                player_id = str(get_player_id(path))

                dct_data[STR_HOME][player_id] =  {}
                dct_data[STR_HOME][player_id][STR_PATH] = path

                tpl_work += ([player_id, STR_HOME, path],)

                if dct_data[STR_HOME].get(STR_NUMBER_OF_ELEMENTS) == None:
                    dct_data[STR_HOME][STR_NUMBER_OF_ELEMENTS] = 1
                else:
                    dct_data[STR_HOME][STR_NUMBER_OF_ELEMENTS] = int(dct_data[STR_HOME][STR_NUMBER_OF_ELEMENTS]) + 1
                
                number_of_elements += 1          
            elif STR_AWAY in path:
                #not the properties file
                player_id = str(get_player_id(path))
                
                dct_data[STR_AWAY][player_id] =  {}
                dct_data[STR_AWAY][player_id][STR_PATH] = path

                tpl_work += ([player_id, STR_AWAY, path],)
                
                if dct_data[STR_AWAY].get(STR_NUMBER_OF_ELEMENTS) == None:
                    dct_data[STR_AWAY][STR_NUMBER_OF_ELEMENTS] = 1
                else:
                    dct_data[STR_AWAY][STR_NUMBER_OF_ELEMENTS] = int(dct_data[STR_AWAY][STR_NUMBER_OF_ELEMENTS]) + 1
                
                number_of_elements += 1
            elif STR_BALL in path:
                #not the properties file
                player_id = str(get_player_id(path))

                dct_data[STR_BALL][player_id] =  {}
                dct_data[STR_BALL][player_id][STR_PATH] = path
                
                tpl_work += ([player_id, STR_BALL, path],)

                if dct_data[STR_BALL].get(STR_NUMBER_OF_ELEMENTS) == None:
                    dct_data[STR_BALL][STR_NUMBER_OF_ELEMENTS] = 1
                else:
                    dct_data[STR_BALL][STR_NUMBER_OF_ELEMENTS] = int(dct_data[STR_BALL][STR_NUMBER_OF_ELEMENTS]) + 1
                
                number_of_elements += 1
            else:
                dct_data[STR_OTHER][player_id] =  {}
                dct_data[STR_OTHER][player_id][STR_PATH] = path
                
                if dct_data[STR_OTHER].get(STR_NUMBER_OF_ELEMENTS) == None:
                    dct_data[STR_OTHER][STR_NUMBER_OF_ELEMENTS] = 1
                else:
                    dct_data[STR_OTHER][STR_NUMBER_OF_ELEMENTS] = int(dct_data[STR_OTHER][STR_NUMBER_OF_ELEMENTS]) + 1
                
                number_of_elements += 1
            
    dct_data[STR_NUMBER_OF_ELEMENTS] = number_of_elements
    dct_data[STR_WORK] = tpl_work
    return(dct_data)

# get the player id back from the filename
# 1.csv -> player id = 1
def get_player_id(str_filepath, str_suffix='.csv'):
    return(str_filepath[str_filepath.rfind('\\')+1:-len(str_suffix)])
    
def get_properties(str_filepath, str_parameter):
    with open(str_filepath, 'r') as f:
        lines = f.readlines() 
  
        # Strips the newline character 
        for line in lines:
            if str_parameter in line:
                return(line[line.find('"')+1:].strip()[:-1])
    return('')

def main():
    start_time = time.perf_counter()
    
    print('{} - Preparing data - start'.format(time.perf_counter()))
    
    #create json object out of the files
    # '..' -> one folder up
    dct_data = create_data_json(os.path.join(os.path.dirname( __file__ ), 'data'))
    #write to file
    #with open(os.path.join(os.getcwd(), 'game.json'), 'w') as outfile:
    #    json.dump(dct_data, outfile)

    # Open game JSON file
    #with open(os.path.join(os.getcwd(), 'game.json')) as json_file: 
    #    dct_data = json.load(json_file) 

    #create topics if not existent
    #for kafka_topic in kafka_topics:
    #    #{'__consumer_offsets': TopicMetadata(__consumer_offsets, 50 partitions), '__confluent.support.metrics': TopicMetadata(__confluent.support.metrics, 1 partitions), 'test-topic': TopicMetadata(test-topic, 1 partitions)}
    #    #print(kafka_topics_get('kafka-1', '9092'))
    #    if len([elem for elem in kafka_topics_get('kafka-1', '9092') if elem == kafka_topic]) == 0:
    #            #create kafka topic(s)
    #            print('create kafka topic ('+kafka_topic+') as it does not exist.')
    #            kafka_topics_create('kafka-1', '9092', [kafka_topic])

    #list of parameters that are give to each process (tuple of lists)
    params = [] 

    # dct_data[STR_WORK] -> tuple of lists. of the structure below
    # ["7", "home", "C:\\Users\\pasca\\HV\\github\\SemesterarbeitCASBGD\\data\\home\\7.csv"]

    for elem in dct_data[STR_WORK]:
        temp = elem
        #add kafka topic at the end to each list element 
        temp.append(kafka_topics[0])

        #add dct_data to params list
        temp.append(dct_data[STR_CONFIG_PROPERTIES])

        #define kafka broker list
        temp.append(kafka_brokers)
        
        #add to parameter list
        params.append(temp)

    
    #convert to tuple
    params = tuple(params)
  
    print('{} - Preparing data - end'.format(time.perf_counter()))

    start_time = time.perf_counter()
    print('{} - Starting to send data in parallel - start'.format(time.perf_counter()))

    # 2 x 11 players and the ball -> 23
    num_processes = int(dct_data[STR_NUMBER_OF_ELEMENTS])
    #print('num of processes:', num_processes)

    with Pool(processes=num_processes) as pool:
        pool.map(execute_log_data, params)
        #pass
    
    print('{} - Starting to send data in parallel - end'.format(time.perf_counter()))

    end_time = time.perf_counter()
    print(start_time, end_time)
    print('{} - Took: {} s'.format(time.perf_counter(), end_time - start_time))

if __name__ == "__main__":
    main()