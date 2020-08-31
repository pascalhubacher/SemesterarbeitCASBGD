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

app = faust.App('worker_test', broker='kafka://kafka-1:9092', topic_partitions=1, value_serializer='raw')
game_event_topic = app.topic('test_topic', value_type=GameEvent)
#out_topic =  = app.topic('test_topic1', value_type=GameEvent)

@app.agent(game_event_topic)
async def process(stream):
    async for values in stream.take(75, within=3):
        print(f'RECEIVED {len(values)}: {values}')

#if __name__ == '__main__':
#    app.main()


