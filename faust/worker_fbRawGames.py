import faust
import time, math

def whatsTheBallId(metadataTopic):
    return('200')

def whatsTheMatchId(metadataTopic):
    return('19060518')

def ballPossession(playerId, ballId, distance=3):
    dist = euclidianDistance((ballId[0], ballId[1], ballId[2]),(playerId[0], playerId[1], playerId[2]))
    #distance below 3 meters count as ball possession
    if dist < 3:
        return((True, dist))
    else:
        return(False, -1)

def euclidianDistance(ball_set, player_set):
    return(math.sqrt((float(ball_set[0]) - float(player_set[0]))**2 + (float(ball_set[1]) - float(player_set[1]))**2 + (float(ball_set[2]) - float(player_set[2]))**2))

#GLOBALS
ballPossessionDistance = 3
BALL_ID = whatsTheBallId('rawMetaMatch')
MATCH_ID = whatsTheMatchId('rawMetaMatch')
BALL_KEY = str(MATCH_ID)+'.'+str(BALL_ID)

#variables
#list of all kafka brokers
#kafka_brokers = ['kafka-1:9092', 'kafka-2:9093', 'kafka-3:9094']
kafka_brokers = ['kafka-1:9092']
kafka_topics = ['rawGames', 'fbBallPossession', 'rawMetaMatch']

windows_size = 1 #second
events_per_second = 25
number_of_players_plus_ball = 23
#max_events = windows_size * events_per_second * number_of_players_plus_ball
#print('windows_size', windows_size)
#print('max_events', max_events)

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

# GameEvent Schema
class GameEvent(faust.Record, serializer='json'):
    ts: str
    x: str
    y: str
    z: str
    id: str
    matchid: str

app = faust.App('faustFbrawGames', broker=kafka_brokers, topic_partitions=int(len(kafka_brokers)), value_serializer='raw')
#topic all the events of all games are sent to it
rawGameTopic = app.topic('rawGames', value_type=GameEvent)
#topic to write into it if a player is close to the ball
fbCloseToBallTopic = app.topic('fbBallPossession', value_type=GameEvent)
#Table to save the latest element of each player and the ball
ballPossessionTable = app.Table('ballPossessionTable', default=GameEvent)

@app.agent(rawGameTopic)
async def process(stream):
    async for key, value in stream.items():
        #only work with the elements of the MATCH_ID
        if key.decode("utf-8").split('.')[0] == MATCH_ID:
            #print('--START--')
            
            #write the element to the table 'ballPossessionTable'
            ballPossessionTable[key] = value

            #print(ballPossessionTable.keys())
            #print(ballPossessionTable.values())

            if key == bytes(BALL_KEY, 'utf-8'):
                ball = ballPossessionTable[bytes(BALL_KEY, 'utf-8')]
                #print(ball)
                elements = []
                for key_elem, value_elem in zip(ballPossessionTable.keys(), ballPossessionTable.values()):
                    if not (key_elem == bytes(BALL_KEY, 'utf-8')) and not (str(value_elem) == ''):
                        #print('--key--')
                        #print(key_elem)
                        dist = ballPossession((value_elem.x, value_elem.y, value_elem.z), (ball.x, ball.y, ball.z), distance=ballPossessionDistance)
                        if dist[0]:
                            #create list element in a set
                            elements.append((key_elem, value_elem, dist[1]))

                if not len(elements) == 0:
                    #print('---if--')
                    #print(elements)
                    #write to 'fbBallPossession' topic
                    # if more than 1 player is close to the ball then the closest has ball possession
                    best = elements[0]
                    for elem in elements:
                        if elem[2] < best[2]:
                            best = elem
                    #print(best)

                    #send record to topic 'fbCloseToBallTopic'
                    await fbCloseToBallTopic.send(key=bytes(str(best[0]), 'utf-8'), value=GameEvent(ts=best[1].ts, x=best[1].x, y=best[1].y, z=best[1].z, id=best[1].id, matchid=best[1].matchid))

            #timer 3sec
            #80% ball possession -> write topic -> ball posession state



            ##if the ball value is in the table
            #value = str(windowedTable[bytes(BALL_KEY, 'utf-8')].value())
            #if not value == '':
            #    print('BALL - '+str(bytes(BALL_KEY, 'utf-8'))+' - '+str(windowedTable[bytes(BALL_KEY, 'utf-8')].value()))
            #    #print('BALL - '+str(getxyzvalues(str(windowedTable[bytes(BALL_KEY, 'utf-8')].value()))))

            #    for key_elem in list(windowedTable.keys()):
            #        #do not take the ball data
            #        if not (key_elem == bytes(BALL_KEY, 'utf-8')) and not (windowedTable[key_elem].value() == ''):
            #            euclidian_distance = euclidianDistance(getxyzvalues(str(windowedTable[bytes(BALL_KEY, 'utf-8')].value())),getxyzvalues(str(windowedTable[key_elem].value())))
            #            print(str(key_elem)+' - '+str(windowedTable[key_elem].value())+' - '+str(euclidian_distance))
            #            #print(getxyzvalues(str(windowedTable[bytes(BALL_KEY, 'utf-8')].value())))
            #            #print(getxyzvalues(str(windowedTable[key_elem].value())))
            #            if euclidian_distance < 3:
            #                await fbCloseToBallTopic.send(key=key_elem, value=windowedTable[key_elem].value())

            #print('----')
            # Show items present relative to time of current event in stream:
            #print(list(windowedTable.items()))

            #print('----')
            # Show values present relative to time of current event in stream:
            #print(list(windowedTable.values()))

            #print('--END--')
    #    async for values in stream.take(max_events, within=windows_size):
    #        print(f'RECEIVED {len(values)} with key xy')

# app2 = faust.App('faustFbTableBallPossession', broker=kafka_brokers, topic_partitions=int(len(kafka_brokers)), value_serializer='raw')
# @app2.agent(fbCloseToBallTopic)
# @app2.timer(3.0)
# async def my_periodic_task():
#     print('THREE SECONDS PASSED')
#     # async def process2(stream2):
#     # #async for key, value in stream.items():
#     #     async for elements in stream2.take(100, within=3.0):
#     #         print(elements)

# if __name__ == '__main__':
#     app.main()


