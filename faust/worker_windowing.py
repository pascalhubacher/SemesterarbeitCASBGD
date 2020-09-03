import faust
import time

#variables
windows_size = 3
events_per_second = 25
number_of_players_plus_ball = 23
max_events = windows_size * events_per_second * number_of_players_plus_ball
print('windows_size', windows_size)
print('max_events', max_events)

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

app = faust.App('faustFbWindowing', broker='kafka://kafka-1:9092', topic_partitions=1, value_serializer='raw')
rawGameTopic = app.topic('rawGames', value_type=GameEvent)

@app.agent(rawGameTopic)
async def process(stream):
    async for values in stream.take(max_events, within=windows_size):
        print(f'RECEIVED {len(values)}: {values[0].GameEvent.ts}')

#if __name__ == '__main__':
#    app.main()


