import faust
import math, time
from datetime import datetime, timedelta 

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

# calculate the euclidian distance between two points in a 3 dimensional vector space
def euclidianDistance(point1, point2):
    return(math.sqrt((float(point1[0]) - float(point2[0]))**2 + (float(point1[1]) - float(point2[1]))**2 + (float(point1[2]) - float(point2[2]))**2))

#calculates the delta distance of x,y,z 
def calcDeltaDistance(pointNew, pointOld):
    #point1 and 2 must be formatted as a set like this (x, y, z)
    #x, y, z float
    
    # xNew - xOld
    # yNew - yOld
    # zNew - zOld
    return((float(pointNew[0])-float(pointOld[0]), float(pointNew[1])-float(pointOld[1]), float(pointNew[2])-float(pointOld[2])))

#calculates the time delta in microseconds
def calcDeltaTime(timestampNew, timestampOld):
    #timestamps must be formatted as ISO8601 string Timestamp
    # ts -> deltatime in microseconds
    return((datetime.strptime(str(timestampNew), '%Y.%m.%dT%H:%M:%S.%f')-datetime.strptime(str(timestampOld), '%Y.%m.%dT%H:%M:%S.%f')).microseconds)

#calculates the velocity -> math: velocity = delta distance [m] / delta time [s] (linear velocity)
def calcVelocity(pointNew, pointOld):
    #point1 and 2 must be formatted as a set like this (x, y, z, ts)
    #timeDelta is in microseconds
    timeDelta = calcDeltaTime(pointNew[3],pointOld[3])/1000/1000
    #timedelta must be bigger than 0
    if float(timeDelta) > 0:
        return(euclidianDistance((pointNew[0], pointNew[1], pointNew[2]), (pointOld[0], pointOld[1], pointOld[2]))/(timeDelta))
    else:
        return('NaN')

#calculates the acceleration -> math: acceleration = delta velocity [m/s]/ delta time [s] (linear acceleration)
def calcAcceleration(advancedInfoNew, advancedInfoOld):
    #point1 and 2 must be formatted as a set like this 
    #ts [str], velocity [float], acceleration[float], distance[str], directionVector[set], id[int], matchid[int])

    #returns float [m/s^2]
    return((advancedInfoNew.velocity - advancedInfoOld.velocity) / (calcDeltaTime(advancedInfoNew.ts, advancedInfoOld.ts)/1000/1000))

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
    x: float
    y: float
    z: float
    id: int
    matchid: int

# GameEvent Schema
class AdvancedInfo(faust.Record, serializer='json'):
    ts: str
    velocity: float #[m/s]
    acceleration: float #[m/s^2]
    distance: float #[m]
    directionVector: str #(x, y, z)
    id: int
    matchid: int

app = faust.App('faustFbRawGames', broker=kafka_brokers, topic_partitions=int(len(kafka_brokers)), value_serializer='raw')
#topic all the events of all games are sent to it
rawGameTopic = app.topic('rawGames', value_type=GameEvent)

#topic to write into it if a player is close to the ball
fbBallPossessionTopic = app.topic('fbBallPossession', value_type=GameEvent)

#topic to write more advanced information about an element (need two elements to calculate them)
fbAdvancedInfosTopic = app.topic('fbAdvancedInfos', value_type=AdvancedInfo)

#Table to save the latest element of each player and the ball
fbAdvancedInfosTable = app.Table('fbAdvancedInfosTable', default=AdvancedInfo)

#Table to save the latest element of each player and the ball
fbBallPossessionTable = app.Table('fbBallPossessionTable', default=GameEvent)

@app.agent(rawGameTopic)
async def process(stream):
    async for key, value in stream.items():
        #only work with the elements of the MATCH_ID
        if key.decode("utf-8").split('.')[0] == MATCH_ID:
            #print('--START--')
            
            #only calculate the advanced parameters if an existing value is in the table
            if key in fbBallPossessionTable:
                pointOld = (fbBallPossessionTable[key].x, fbBallPossessionTable[key].y, fbBallPossessionTable[key].z, fbBallPossessionTable[key].ts)
                pointNew = (value.x, value.y, value.z, value.ts)

                #calculates the delta of all elements in the set (x,y,z,ts[us])
                delta_vectorNew = calcDeltaDistance(pointNew, pointOld)  
                #print(pointNew, pointOld)
                velocityNew = calcVelocity(pointNew, pointOld)           

                if key in fbAdvancedInfosTable:
                    #acceleration can be calculated as an earlier velocity (delta velocity needed) exists
                    advancedInfoOld = fbAdvancedInfosTable[key]
                    advancedInfoNew = AdvancedInfo(ts=str(value.ts), velocity=velocityNew, acceleration=-1, distance=euclidianDistance(pointNew, pointOld), directionVector=delta_vectorNew, id=value.id, matchid=value.matchid)
                    accelerationNew = calcAcceleration(advancedInfoNew, advancedInfoOld)
                    
                    #write new element to the table
                    fbAdvancedInfosTable[key] = AdvancedInfo(ts=value.ts, velocity=velocityNew, acceleration=accelerationNew, distance=euclidianDistance(pointNew, pointOld), directionVector=delta_vectorNew, id=value.id, matchid=value.matchid)
                    
                    #write element to topic fbAdvancedInfos
                    await fbAdvancedInfosTopic.send(key=key, value=AdvancedInfo(ts=str(value.ts), velocity=velocityNew, acceleration=accelerationNew, distance=euclidianDistance(pointNew, pointOld), directionVector=delta_vectorNew, id=value.id, matchid=value.matchid))


                else:
                    #write new element to the table
                    #if no accelleration can be calculated -1 is used
                    fbAdvancedInfosTable[key] = AdvancedInfo(ts=str(value.ts), velocity=velocityNew, acceleration=-1, distance=euclidianDistance(pointNew, pointOld), directionVector=delta_vectorNew, id=value.id, matchid=value.matchid)

                

            #write the element to the table 'fbBallPossessionTable'
            fbBallPossessionTable[key] = value

            #print(fbBallPossessionTable.keys())
            #print(fbBallPossessionTable.values())

            #if ball key
            if key == bytes(BALL_KEY, 'utf-8'):
                ball = fbBallPossessionTable[bytes(BALL_KEY, 'utf-8')]
                #print(ball)
                elements = []
                for key_elem, value_elem in zip(fbBallPossessionTable.keys(), fbBallPossessionTable.values()):
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

                    #send record to topic 'fbBallPossessionTopic'
                    await fbBallPossessionTopic.send(key=bytes(str(best[0]), 'utf-8'), value=GameEvent(ts=str(best[1].ts), x=float(best[1].x), y=float(best[1].y), z=float(best[1].z), id=int(best[1].id), matchid=int(best[1].matchid)))

# if __name__ == '__main__':
#     app.main()