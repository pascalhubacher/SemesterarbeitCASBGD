import faust
from datetime import timedelta

def whatsTheBallId(metadataTopic):
    return('200')

def ballPossession(playerId, ballId, distance=2):
    return(True)

#json data in the stream
#key=19060518.20
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

app = faust.App('faustRawGames', broker='kafka://kafka-1:9092', topic_partitions=1, value_serializer='raw')

rawGameTopic = app.topic('rawGames', value_type=GameEvent)

fbCloseToBallTopic = app.topic('fbBallPossession', value_type=GameEvent)

event_counter = app.Table('event_count', default=int)

#look at stream rawGames
@app.agent(rawGameTopic)
async def processS(rawGamesEvents: faust.Stream[GameEvent]):
    async for key, gameEvent in rawGamesEvents.items():
        #print(key)
        #print(gameEvent)

        #send event to topic
        #await fbCloseToBallTopic.send(key=key, value=gameEvent)

#if __name__ == '__main__':
#    app.main()