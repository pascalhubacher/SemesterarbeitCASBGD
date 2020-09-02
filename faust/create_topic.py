from confluent_kafka import Producer, Consumer, admin
#Admin -> get/create/delete topics
from confluent_kafka.admin import AdminClient, NewTopic

#create kafka topics
def kafka_topics_create(ip, port, topic_list):
    a = AdminClient({
        'bootstrap.servers': ip+':'+port
    })

    new_topics = [NewTopic(topic, num_partitions=1, replication_factor=1) for topic in topic_list]
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
def kafka_topics_get(ip, port):
    kadmin = AdminClient({
        'bootstrap.servers': ip+':'+port
    })

    #Returns a dict(). See example below.
    #{'topic01': TopicMetadata(topic01, 3 partitions),}
    return(kadmin.list_topics().topics)

#variables
#'fbPenaltybox', 'fbPitchRight'
kafka_topics = ['rawGames'] 

for kafka_topic in kafka_topics:
    #create topic if not existent
    #{'__consumer_offsets': TopicMetadata(__consumer_offsets, 50 partitions), '__confluent.support.metrics': TopicMetadata(__confluent.support.metrics, 1 partitions), 'test-topic': TopicMetadata(test-topic, 1 partitions)}
    #print(kafka_topics_get('kafka-1', '9092'))
    if len([elem for elem in kafka_topics_get('kafka-1', '9092') if elem == kafka_topic]) == 0:
        #create kafka topic(s)
        kafka_topics_create('kafka-1', '9092', [kafka_topic])
        print('kafka topic ('+kafka_topic+') created.')
    else:
        print('kafka topic ('+kafka_topic+') already exists.')