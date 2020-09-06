import faust
import time, math

def whatsTheBallId(metadataTopic):
    return('200')

def whatsTheMatchId(metadataTopic):
    return('19060518')

def ballPossession(playerId, ballId, distance=2):
    return(True)

def getxyzvalues(GameEventStr):
    #print(GameEventStr)
    x = GameEventStr.split(',')[1].split("'")[1].strip()
    y = GameEventStr.split(',')[2].split("'")[1].strip()
    z = GameEventStr.split(',')[3].split("'")[1].strip()
    return((x,y,z))

def euclidianDistance(ball_set, player_set):
    return(math.sqrt((float(ball_set[0]) - float(player_set[0]))**2 + (float(ball_set[1]) - float(player_set[1]))**2 + (float(ball_set[2]) - float(player_set[2]))**2))

#GLOBALS
BALL_ID = whatsTheBallId('rawMetaMatch')
MATCH_ID = whatsTheMatchId('rawMetaMatch')
BALL_KEY = str(MATCH_ID)+'.'+str(BALL_ID)

#variables
windows_size = 1 #second
events_per_second = 25
number_of_players_plus_ball = 23
max_events = windows_size * events_per_second * number_of_players_plus_ball
print('windows_size', windows_size)
print('max_events', max_events)

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

app = faust.App('faustFbWindowing', broker='kafka://kafka-1:9092', topic_partitions=1, value_serializer='raw')
rawGameTopic = app.topic('rawGames', value_type=GameEvent)
fbCloseToBallTopic = app.topic('fbBallPossession', value_type=GameEvent)

from datetime import timedelta
windowedTable = app.Table('windowedTable', default=str).tumbling(1, expires=timedelta(seconds=1), key_index=True)
#windowedTable = app.Table('windowedTable', value_type=GameEvent).tumbling(1, expires=timedelta(seconds=1), key_index=True)

@app.agent(rawGameTopic)
async def process(stream):
    async for key, value in stream.items():
        #print(key, value)
        windowedTable[key] = value

        print('--START--')
        #print(str(bytes(BALL_KEY, 'utf-8'))+' - '+str(windowedTable[bytes(BALL_KEY, 'utf-8')].value()))

        # Show keys present relative to time of current event in stream:
        #print(len(list(windowedTable.keys())), list(windowedTable.keys()))
        
        #if the ball value is in the table
        value = str(windowedTable[bytes(BALL_KEY, 'utf-8')].value())
        if not value == '':
            print('BALL - '+str(bytes(BALL_KEY, 'utf-8'))+' - '+str(windowedTable[bytes(BALL_KEY, 'utf-8')].value()))
            #print('BALL - '+str(getxyzvalues(str(windowedTable[bytes(BALL_KEY, 'utf-8')].value()))))

            for key_elem in list(windowedTable.keys()):
                #do not take the ball data
                if not (key_elem == bytes(BALL_KEY, 'utf-8')) and not (windowedTable[key_elem].value() == ''):
                    print(str(key_elem)+' - '+str(windowedTable[key_elem].value())+' - '+str(euclidianDistance(getxyzvalues(str(windowedTable[bytes(BALL_KEY, 'utf-8')].value())),getxyzvalues(str(windowedTable[key_elem].value())))))
                    #print(getxyzvalues(str(windowedTable[bytes(BALL_KEY, 'utf-8')].value())))
                    #print(getxyzvalues(str(windowedTable[key_elem].value())))
                    

        #print('----')
        # Show items present relative to time of current event in stream:
        #print(list(windowedTable.items()))

        #print('----')
        # Show values present relative to time of current event in stream:
        #print(list(windowedTable.values()))

        print('--END--')
#    async for values in stream.take(max_events, within=windows_size):
#        print(f'RECEIVED {len(values)} with key xy')



#if __name__ == '__main__':
#    app.main()


