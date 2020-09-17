import faust
import time, datetime, math, json, os

def whatsTheBallId(metadataTopic):
    return('200')

def whatsTheMatchId(metadataTopic):
    return('19060518')

def ballPossession(playerId, ballId, distance=3):
    dist = euclidianDistance((ballId[0], ballId[1], ballId[2]),(playerId[0], playerId[1], playerId[2]))
    if dist < 3:
        return((True, dist))
    else:
        return(False)

def euclidianDistance(ball_set, player_set):
    return(math.sqrt((float(ball_set[0]) - float(player_set[0]))**2 + (float(ball_set[1]) - float(player_set[1]))**2 + (float(ball_set[2]) - float(player_set[2]))**2))

# (True, properties in json format) -> if id found
# (False, None) -> if not found
def getListOfPropertiesOfItem(str_json, element):
    #json_str = json.loads(str_json)
    if not str_json.get(element) == None:
        #found
        return((True, str_json.get(element)))
    else:
        #not found
        return((False, None))

#GLOBALS
BALL_ID = whatsTheBallId('rawMetaMatch')
MATCH_ID = whatsTheMatchId('rawMetaMatch')
BALL_KEY = str(MATCH_ID)+'.'+str(BALL_ID)
#who had the Ball in the last event
BALL_POSSESSION_ID = str(MATCH_ID)

# Open playser JSON file
with open(os.path.join(os.getcwd(), 'player.json')) as json_file: 
    player_data = json.load(json_file)

#variables
#list of all kafka brokers
#kafka_brokers = ['kafka-1:9092', 'kafka-2:9093', 'kafka-3:9094']
kafka_brokers = ['kafka-1:9092']
kafka_topics = ['rawGames', 'fbBallPossession', 'rawMetaMatch']

windows_size = 1 #second
events_per_second = 25
number_of_players_plus_ball = 23
#max_events = windows_size * events_per_second * number_of_players_plus_ball
max_elements_in_window = windows_size * events_per_second

ball_possession_threshold = 0.5

print('windows_size', windows_size)
print('max_events', max_elements_in_window)
print('ddddd', BALL_POSSESSION_ID)

#json data in the stream
#key=19060518.10
#value={
#  "ts": "2018-06-29T08:15:27.243860",
#  "x": "-0.38",
#  "y": "-2.23",
#  "z": "0.0",
#  "id": "10"
#  "matchid": "19060518"
#}

#, serializer='json'
class GameEvent(faust.Record, serializer='json'):
    ts: str
    x: str
    y: str
    z: str
    id: str
    matchid: str

#, serializer='json'
class GameState(faust.Record, serializer='json'):
    ts: str
    eventtype: str
    matchid: str
    description: str
#BallPossessionChange (json in the description field)
#playerId, playerName, playerAlias, objectType (0-> Ball, 1-> Home, 2->Away)

app = faust.App('faustFbfbBallPossession', broker=kafka_brokers, topic_partitions=int(len(kafka_brokers)), value_serializer='raw')
#app2 = faust.App('faustFbTableBallPossession3', broker=kafka_brokers, topic_partitions=int(len(kafka_brokers)), value_serializer='raw')
#fbCloseToBallTopic = app2.topic('fbBallPossession', value_type=GameEvent)

#topic to listen to
fbCloseToBallTopic = app.topic('fbBallPossession', value_type=GameEvent)

#Table to save the latest element of each player and the ball
ballPossessionTable = app.Table('ballPossessionTable2', value_type=GameEvent).tumbling(datetime.timedelta(seconds=windows_size), expires=datetime.timedelta(seconds=windows_size))

#topic to write for all Events that are shown
fbEvents = app.topic('fbEvents', value_type=GameState)

#last ball time stamp
time_stamp = ''

@app.agent(fbCloseToBallTopic)
async def process(stream):
    async for records in stream.take(max_elements_in_window, within=windows_size):
        print('-----'+str(max_elements_in_window)+'-----')

        #print(len(records))
        #<GameEvent: ts='2019.06.05T20:45:14.320000', x='-33.53', y='-11.4', z='0.0', id='3', matchid='19060518'>
        counter_dict = {}
        for record in records:
            #get timestamp
            time_stamp = record.ts
            if record.id in counter_dict.keys():
                counter_dict[record.id] += 1
            else:
                counter_dict[record.id] = 1
        #create sorted list (ascending) of sets (id, count)
        sorted_list = sorted(counter_dict.items(), key=lambda kv: kv[1])

        if not len(sorted_list) == 0:
            #only create an event if the player is < 3m to the ball and is the closes for 70% of the time within the three seconds
            # # of times the player was the closest to the ball and within 3m / max of elements possible in a window -> must be bigger than the threshold
            if float(sorted_list[-1][1])/float(max_elements_in_window) >= ball_possession_threshold:
                # Topic BallPossessionChange 
                print(sorted_list)
                                
                #set variable to global
                global BALL_POSSESSION_ID

                #is there player information for the match id and player id
                if not BALL_POSSESSION_ID == str(MATCH_ID)+'.'+str(sorted_list[-1][0]):
                    #last player with ball possession
                    BALL_POSSESSION_ID = str(MATCH_ID)+'.'+str(sorted_list[-1][0])
                    if getListOfPropertiesOfItem(player_data, str(MATCH_ID)+'.'+str(sorted_list[-1][0]))[0]:
                        player_info = getListOfPropertiesOfItem(player_data, str(MATCH_ID)+'.'+str(sorted_list[-1][0]))[1]
                        print(json.dumps(player_info), time_stamp)
                        
                        #sent record to topic 'fbEvents'
                        #"<GameState: ts='2019.06.05T20:45:14.320000', eventtype='BallPossessionChange', matchid='19060518', description="
                        await fbEvents.send(key=bytes(str(MATCH_ID), 'utf-8'), value=GameState(ts=str(time_stamp), eventtype=str('BallPossessionChange'), matchid=str(MATCH_ID), description=str(json.dumps(player_info))))
                else:
                    print('Same player as before')

        print('-----')

@app.agent(fbEvents)
async def process(stream2):
    async for key2, value2 in stream2.items():
        print(key2, value2)
#    async for key, value in stream.items():
#         #only work with the elements of the MATCH_ID
#         if key.decode("utf-8").split('.')[0] == MATCH_ID:
#             #print('--START--')
            
#             #write the element to the table 'ballPossessionTable'
#             ballPossessionTable[key] = value

#             #print(ballPossessionTable.keys())
#             #print(ballPossessionTable.values())

#             if key == bytes(BALL_KEY, 'utf-8'):
#                 ball = ballPossessionTable[bytes(BALL_KEY, 'utf-8')]
#                 elements = []
#                 for key_elem, value_elem in zip(ballPossessionTable.keys(), ballPossessionTable.values()):
#                     if not (key_elem == bytes(BALL_KEY, 'utf-8')) and not (str(value_elem) == ''):
#                         dist = ballPossession((value_elem.x, value_elem.y, value_elem.z), (ball.x, ball.y, ball.z))
#                         if dist[0]:
#                             #create list element in a set
#                             elements.append((key_elem, value_elem, dist[1]))

#                 if not len(elements) == 0:
#                     print(elements)
#                     #write to 'fbBallPossession' topic
#                     # if more than 1 player is close to the ball then the closest has ball possession
#                     best = elements[0]
#                     for elem in elements:
#                         if elem[2] < best[2]:
#                             best = elem
#                     print(best)
#                     await fbCloseToBallTopic.send(key=best[0], value=best[1])

#             #timer 3sec
#             #80% ball possession -> write topic -> ball posession state



#             ##if the ball value is in the table
#             #value = str(windowedTable[bytes(BALL_KEY, 'utf-8')].value())
#             #if not value == '':
#             #    print('BALL - '+str(bytes(BALL_KEY, 'utf-8'))+' - '+str(windowedTable[bytes(BALL_KEY, 'utf-8')].value()))
#             #    #print('BALL - '+str(getxyzvalues(str(windowedTable[bytes(BALL_KEY, 'utf-8')].value()))))

#             #    for key_elem in list(windowedTable.keys()):
#             #        #do not take the ball data
#             #        if not (key_elem == bytes(BALL_KEY, 'utf-8')) and not (windowedTable[key_elem].value() == ''):
#             #            euclidian_distance = euclidianDistance(getxyzvalues(str(windowedTable[bytes(BALL_KEY, 'utf-8')].value())),getxyzvalues(str(windowedTable[key_elem].value())))
#             #            print(str(key_elem)+' - '+str(windowedTable[key_elem].value())+' - '+str(euclidian_distance))
#             #            #print(getxyzvalues(str(windowedTable[bytes(BALL_KEY, 'utf-8')].value())))
#             #            #print(getxyzvalues(str(windowedTable[key_elem].value())))
#             #            if euclidian_distance < 3:
#             #                await fbCloseToBallTopic.send(key=key_elem, value=windowedTable[key_elem].value())

#             #print('----')
#             # Show items present relative to time of current event in stream:
#             #print(list(windowedTable.items()))

#             #print('----')
#             # Show values present relative to time of current event in stream:
#             #print(list(windowedTable.values()))

#             #print('--END--')
#     #    async for values in stream.take(max_events, within=windows_size):
#     #        print(f'RECEIVED {len(values)} with key xy')

#@app.agent(fbCloseToBallTopic)
# @app.timer(3.0)
# async def my_periodic_task():
#     print('THREE SECONDS PASSED')
    # async def process(stream):
    #     async for key, value in stream.items():
    #         print(value)

#if __name__ == '__main__':
#    app.main()