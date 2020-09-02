import faust

app = faust.App(
    'hello-world',
    broker='kafka://kafka-1:9092',
    value_serializer='json',
)

greetings_topic = app.topic('rawGames')

@app.agent(greetings_topic)
async def greet(greetings):
    async for greeting in greetings:
        print(greeting)