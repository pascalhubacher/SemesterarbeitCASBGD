#returns TRUE if the port is listening, False if not
def portscan(hostname, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   
    try:
        s.connect((hostname, port))
        s.close()
        return True
    except:
        return None

#variables
#'fbPenaltybox', 'fbPitchRight'
kafka_topics = ['rawGames', 'fbBallPossession', 'rawMetaMatch']
kafka_broker_name = 'kafka-1'
kafka_broker_port = '9092'

#wait until kafka is running (max 60seconds)
i = 0
while True:
    if (i == 30):
        print(portscan(kafka_broker_name, kafka_broker_port))
        sys.exit(time.ctime() + ' - Error - Kafka ('+kafka_broker_name+':'+kafka_broker_port+') not ready - timed out (stop python program)')

    if portscan(kafka_broker_name, kafka_broker_port):
        print(time.ctime() + ' - Info - Kafka ('+kafka_broker_name+':'+kafka_broker_port+') is ready')
        break
    else:
        time.sleep(2)
        print(time.ctime() + ' - Warning - Kafka ('+kafka_broker_name+':'+kafka_broker_port+') not ready - wait 2 seconds and retry')
        i += 1