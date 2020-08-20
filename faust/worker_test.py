import faust

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

app = faust.App('worker_test', broker='kafka://kafka-1:9092', topic_partitions=1, value_serializer='raw')
#    
#    value_serializer='raw',

game_event_topic = app.topic('test_topic', value_type=GameEvent)

event_counter = app.Table('event_count', default=int)

@app.agent(game_event_topic)
async def process(test_topic: faust.Stream[GameEvent]) -> None:
    async for game_event in test_topic.group_by(GameEvent.id):
        event_counter[game_event.id] += 1

#if __name__ == '__main__':
#    app.main()