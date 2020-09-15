# import faust
import json, os

#import logging
from ksql import KSQLAPI
#logging.basicConfig(level=logging.DEBUG)
client = KSQLAPI(url='http://ksqldb-server-1:8088', timeout=5)

#print(client.ksql('show tables'))

data = []
try:
    query = client.query('SELECT * FROM t_rawMetaPlayer EMIT CHANGES', use_http2=True)
    for idx, item in enumerate(query):
        if item[0] == '{':
            queryId = json.loads(item)['queryId']
            #print(queryId)
        #print(item)
        data.append(item)
        if idx == 23:
            client.close_query(queryId)
except Exception as e:
    print(e)

#rowKey, gameId, sensorId, name, alias, objectType

#['{"queryId":"6e816df2-f9bb-433d-a5a6-6cd91ec5fe82","columnNames":["ROWKEY","GAMEID","SENSORID","NAME","ALIAS","OBJECTTYPE"],"columnTypes":["STRING","BIGINT","INTEGER","STRING","STRING","INTEGER"]}\n', '["19060518.1",19060518,1,"Patricio","A1",1]\n', '["19060518.3",19060518,3,"Pepe","A2",1]\n', '["19060518.4",19060518,4,"Dias","A3",1]\n', '["19060518.5",19060518,5,"Guerreiro","A4",1]\n', '["19060518.7",19060518,7,"Ronaldo","A5",1]\n', '["19060518.10",19060518,10,"Silva","A6",1]\n', '["19060518.14",19060518,14,"Carvalho","A7",1]\n', '["19060518.16",19060518,16,"Fernandes","A8",1]\n', '["19060518.18",19060518,18,"Neves","A9",1]\n', '["19060518.20",19060518,20,"Semedo","A10",1]\n', '["19060518.23",19060518,23,"Felix","A11",1]\n', '["19060518.101",19060518,101,"Sommer","B1",2]\n', '["19060518.102",19060518,102,"Mbabu","B2",2]\n', '["19060518.105",19060518,105,"Akanji","B3",2]\n', '["19060518.108",19060518,108,"Freuler","B4",2]\n', '["19060518.109",19060518,109,"Seferovic","B5",2]\n', '["19060518.110",19060518,110,"Xhaka","B6",2]\n', '["19060518.113",19060518,113,"Rodriguez","B7",2]\n', '["19060518.114",19060518,114,"Zuber","B8",2]\n', '["19060518.117",19060518,117,"Zakaria","B9",2]\n', '["19060518.122",19060518,122,"Schaer","B10",2]\n', '["19060518.123",19060518,123,"Shaqiri","B11",2]\n', '["19060518.200",19060518,200,"Ball","BALL",0]\n']

player_json = {}
#skip first row
for element in data[1:]:
    element = element.strip().replace('[','').replace(']','').split(',')
    #'["19060518.1",19060518,1,"Patricio","A1",1]\n'
    key = element[0]
    print(key)
    player_json[key] = {}
    player_json[key]['playerId'] = element[2]
    player_json[key]['playerName'] = element[3]
    player_json[key]['playerAlias'] = element[4]
    player_json[key]['objectType'] = element[5]

with open(os.path.join(os.getcwd(), 'player.json'), 'w') as outfile:
    json.dump(player_json, outfile)