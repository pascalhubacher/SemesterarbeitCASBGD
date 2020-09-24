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

#variables
#list of all kafka brokers
#kafka_brokers = ['kafka-1:9092', 'kafka-2:9093', 'kafka-3:9094']
kafka_brokers = ['kafka-1:9092']

ballPossessionWindow = 1 #second
ballPossessionThreshold = 0.5

events_per_second = 25
number_of_players_plus_ball = 23
max_elements_in_window = ballPossessionWindow * events_per_second * number_of_players_plus_ball
#max_elements_in_window = ballPossessionWindow * events_per_second

print('ballPossessionWindow', ballPossessionWindow)
print('max_events', max_elements_in_window)

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

#rowkey = "19060518.10"
class GameState(faust.Record, serializer='json'):
    ts: str
    eventtype: str
    playerId: int
    matchId: int
    playerKey: str #"19060518.10"

app = faust.App('faustFbBallPossession', broker=kafka_brokers, topic_partitions=int(len(kafka_brokers)), value_serializer='raw')
#app2 = faust.App('faustFbTableBallPossession3', broker=kafka_brokers, topic_partitions=int(len(kafka_brokers)), value_serializer='raw')
#fbCloseToBallTopic = app2.topic('fbBallPossession', value_type=GameEvent)

#topic to listen to
fbBallPossessionTopic = app.topic('fbBallPossession', value_type=GameEvent)

#Table to save the window elements of each player
#ballPossessionTable = app.Table('ballPossessionTable2', value_type=GameEvent).tumbling(datetime.timedelta(seconds=ballPossessionWindow), expires=datetime.timedelta(seconds=ballPossessionWindow))

#topic to write for all Events that are shown
fbBallPossessionAggregateTopic = app.topic('fbBallPossessionAggregate', value_type=GameState)

#last ball time stamp
time_stamp = ''

@app.agent(fbBallPossessionTopic)
async def process(stream):
    async for records in stream.take(max_elements_in_window, within=ballPossessionWindow):
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
            #only create an event if the player is < 3m to the ball and is the closes for 50% of the time within the three seconds
            # # of times the player was the closest to the ball and within 3m / max of elements possible in a window -> must be bigger than the threshold
            if float(sorted_list[-1][1])/float(max_elements_in_window) >= ballPossessionThreshold:
                # Topic BallPossessionChange 
                print(sorted_list)
                                
                #set variable to global
                global BALL_POSSESSION_ID

                # was the last ball possession player the same as the player now?
                # we only want to create a message if there is a new player in ball possession 
                if not BALL_POSSESSION_ID == str(MATCH_ID)+'.'+str(sorted_list[-1][0]):
                    #last player with ball possession
                    BALL_POSSESSION_ID = str(MATCH_ID)+'.'+str(sorted_list[-1][0])
                    
                    #"<GameState: ts='2019.06.05T20:45:14.320000', eventtype='BallPossessionChange', matchid='19060518', description="
                    #sent record to topic 'fbBallPossessionAggregate'
                    await fbBallPossessionAggregateTopic.send(key=bytes(str(MATCH_ID), 'utf-8'), value=GameState(ts=str(time_stamp), eventtype=str('BallPossessionChange'), playerId=int(sorted_list[-1][0]), matchId=int(MATCH_ID), playerKey=str(BALL_POSSESSION_ID)))
                else:
                    print('Same player as before')

        print('-----')

#if __name__ == '__main__':
#    app.main()