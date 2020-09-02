import faust

#json data in the stream
#{
#  "ts": "40",
#  "x": "-0.38",
#  "y": "-2.23",
#  "z": "0.0",
#  "id": "10"
#}

#, serializer='json'
class GameEvent(faust.Record, serializer='json'):
    ts: str
    x: str
    y: str
    z: str
    id: str

app = faust.App('faustFb', broker='kafka://kafka-1:9092', topic_partitions=1, value_serializer='raw')

rawGameTopic = app.topic('rawGames', value_type=GameEvent)

fbCloseToBallTopic = app.topic('fbCloseToBall', value_type=GameEvent)

event_counter = app.Table('event_count', default=int)

@app.agent(rawGameTopic)
async def process(rawGamesEvents: faust.Stream[GameEvent]):
    async for gameEvent in rawGamesEvents:
        print(gameEvent)
        gameEvent.forward(fbCloseToBallTopic)

#@app.agent(game_event_topic)
#async def process(games_raw: faust.Stream[GameEvent]) -> None:
#    async for game_event in games_raw:
#        print(game_event)

#if __name__ == '__main__':
#    app.main()