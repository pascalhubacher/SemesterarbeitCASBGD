from confluent_kafka import Producer, Consumer, admin
#Admin -> get/create/delete topics
from confluent_kafka.admin import AdminClient, NewTopic
import time
import json
import os

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

#variables
#list of all kafka brokers
#kafka_brokers = ['kafka-1:9092', 'kafka-2:9093', 'kafka-3:9094']
kafka_brokers = ['kafka-1:9092']
#'fbPenaltybox', 'fbPitchRight'
kafka_topics = ['rawGames', 'fbBallPossession']
#kafka_topics = ['rawGames', 'fbBallPossession', 'rawMetaMatch']

#create kafka topics
def kafka_topics_create(broker_list, topic_list):
    kafka_servers_str = ''
    for kafka_srv_elem in broker_list:
        kafka_servers_str += ', ' + kafka_srv_elem
    
    a = AdminClient({
        'bootstrap.servers': kafka_servers_str
    })
    
    new_topics = [NewTopic(topic, num_partitions=int(len(broker_list)), replication_factor=int(len(broker_list))) for topic in topic_list]
    # Note: In a multi-cluster production scenario, it is more typical to use a replication_factor of 3 for durability.

    # Call create_topics to asynchronously create topics. A dict
    # of <topic,future> is returned.
    fs = a.create_topics(new_topics)

    # Wait for each operation to finish.<
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

def get_properties(str_filepath, str_parameter):
    with open(str_filepath, 'r') as f:
        lines = f.readlines() 
  
        # Strips the newline character 
        for line in lines:
            if str_parameter in line:
                return(line[line.find('"')+1:].strip()[:-1])
    return('')

# get the player id back from the filename
# 1.csv -> player id = 1
def get_player_id(str_filepath, str_suffix='.csv'):
    return(str_filepath[str_filepath.rfind('\\')+1:-len(str_suffix)])
    
#create json object out of the files
# '..' -> one folder up
dct_data = create_data_json(os.path.join(os.path.dirname( __file__ ), 'data'))

#write to file
with open(os.path.join(os.getcwd(), 'game.json'), 'w') as outfile:
    json.dump(dct_data, outfile)
    print('game.json written')

time.sleep(20)

for kafka_topic in kafka_topics:
    #create topic if not existent
    #{'__consumer_offsets': TopicMetadata(__consumer_offsets, 50 partitions), '__confluent.support.metrics': TopicMetadata(__confluent.support.metrics, 1 partitions), 'test-topic': TopicMetadata(test-topic, 1 partitions)}
    #print(kafka_topics_get('kafka-1', '9092'))
    if len([elem for elem in kafka_topics_get(kafka_brokers) if elem == kafka_topic]) == 0:
        #create kafka topic(s)
        kafka_topics_create(kafka_brokers, [kafka_topic])
        print('kafka topic ('+kafka_topic+') created.')
    else:
        print('kafka topic ('+kafka_topic+') already exists.')

#fill in the match config data into the rawMetaMatch topic
