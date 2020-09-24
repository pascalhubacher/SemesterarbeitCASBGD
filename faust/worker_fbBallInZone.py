import faust
import json

#rowkey = "19060518.10"
class GameState(faust.Record, serializer='json'):
    ts: str
    eventtype: str
    playerId: int
    matchId: int
    playerKey: str #"19060518.10"
    eventState: int

#Global Variables
#kafka brokers
kafka_brokers = ['kafka-1:9092']

ballPossessionWindow = 1 #second
events_per_second = 25
#the topic "fbBallPossession get at max every 40ms one entry"
max_elements_in_window = ballPossessionWindow * events_per_second

#initial dict of pitch checks
#ISONPITCH, ISPITCHLEFT, ISPENALTYBOXLEFT, ISPENALTYBOXRIGHT, ISGOALLEFT, ISGOALRIGHT
PITCH_DICT = {}
PITCH_DICT['ISONPITCH'] = {}
PITCH_DICT['ISONPITCH']['value'] = 0
PITCH_DICT['ISPITCHLEFT'] = {}
PITCH_DICT['ISPITCHLEFT']['value'] = -1
PITCH_DICT['ISPENALTYBOXLEFT'] = {}
PITCH_DICT['ISPENALTYBOXLEFT']['value'] = 0
PITCH_DICT['ISPENALTYBOXRIGHT'] = {}
PITCH_DICT['ISPENALTYBOXRIGHT']['value'] = 0
PITCH_DICT['ISGOALLEFT'] = {}
PITCH_DICT['ISGOALLEFT']['value'] = 0
PITCH_DICT['ISGOALRIGHT'] = {}
PITCH_DICT['ISGOALRIGHT']['value'] = 0

#Faust part
#application
app = faust.App('faustFbBallInZone', broker=kafka_brokers, topic_partitions=int(len(kafka_brokers)), value_serializer='json')

#source topic
fbBallInZoneTopic = app.topic('fbBallInZone')

#{
#  "TS": "2019.06.05T20:45:00.040000",
#  "X": -0.62,
#  "Y": -2.32,
#  "ID": 200,
#  "MATCHID": 19060518,
#  "NAME": "Ball",
#  "ISONPITCH": 1,
#  "ISPITCHLEFT": 1,
#  "ISPENALTYBOXLEFT": 0,
#  "ISPENALTYBOXRIGHT": 0,
#  "ISGOALLEFT": 0,
#  "ISGOALRIGHT": 0
#}

#destination topic
fbBallInZoneEventTopic = app.topic('fbBallInZoneEvent', value_type=GameState)

# loop over the stream
@app.agent(fbBallInZoneTopic)
async def process(stream):
    async for key, value in stream.items():
        #only work with the elements of the MATCH_ID
        #if key.decode("utf-8") == MATCH_ID:
        
        #set variable to global
        global PITCH_DICT
        #print(PITCH_DICT)

        #ISONPITCH, ISPITCHLEFT, ISPENALTYBOXLEFT, ISPENALTYBOXRIGHT, ISGOALLEFT, ISGOALRIGHT
        for dict_key, dict_elem in PITCH_DICT.items():
            
            if not str(value[dict_key]) == str(PITCH_DICT[dict_key]['value']):
                #print(str(key)+'---'+str(value[key]))
                #print(str(key)+'---'+str(PITCH_DICT[key]['value']))    
                PITCH_DICT[dict_key]['value'] = str(value[dict_key])
                #print(GameState(ts=str(value['TS']), eventtype=str(key)+'.'+str(value[key]), playerId=int(value['ID']), matchId=int(value['MATCHID']), playerKey=str(value['MATCHID'])+'.'+str(value['ID'])))
                #send record to topic 'fbPitch'
                await fbBallInZoneEventTopic.send(key=bytes(str(value['MATCHID']), 'utf-8'), value=GameState(ts=str(value['TS']), eventtype=str(dict_key), eventState=int(value[dict_key]), playerId=int(value['ID']), matchId=int(value['MATCHID']), playerKey=str(value['MATCHID'])+'.'+str(value['ID'])))
        
#if __name__ == '__main__':
#    app.main()