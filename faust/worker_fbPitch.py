import faust

def whatsTheBallId(metadataTopic):
    return('200')

def whatsTheMatchId(metadataTopic):
    return('19060518')

#GameEvent Schema
class GameEvent(faust.Record, serializer='json'):
    ts: str
    x: float
    y: float
    z: float
    id: int
    matchid: int

#Global Variables
#kafka brokers
kafka_brokers = ['kafka-1:9092']

#get match id
MATCH_ID = whatsTheMatchId('rawMetaMatch')

#list of pitch checks
#isOnPitch, isPitchLeft, isPenaltyBoxLeft, isPenaltyBoxRight, isGoalLeft, goalRight
PITCH_LST = [None, None, None, None, None, None]

#Faust part
#application
app = faust.App('faustFbPitch', broker=kafka_brokers, topic_partitions=int(len(kafka_brokers)), value_serializer='raw')

#source topic
rawGameTopic = app.topic('rawGames', value_type=GameEvent)
#destination topic
fbPitchTopic = app.topic('fbPitch', value_type=GameEvent)

# loop over the stream
@app.agent(rawGameTopic)
async def process(stream):
    async for key, value in stream.items():
        #only work with the elements of the MATCH_ID
        if key.decode("utf-8").split('.')[0] == MATCH_ID:
        
            #set variable to global
            global PITCH_LST
            
            #send record to topic 'fbPitch'
            await fbPitchTopic.send(key=bytes(str(best[0]), 'utf-8'), value=GameEvent(ts=str(best[1].ts), x=float(best[1].x), y=float(best[1].y), z=float(best[1].z), id=int(best[1].id), matchid=int(best[1].matchid)))
        
#if __name__ == '__main__':
#    app.main()