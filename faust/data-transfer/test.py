import faust
# import json

# text = '{"19060518.200": {"playerId": "200", "playerName": "Ball", "playerAlias": "BALL", "objectType": "0"}, "19060518.1": {"playerId": "1", "playerName": "Patricio", "playerAlias": "A1", "objectType": "1"}, "19060518.3": {"playerId": "3", "playerName": "Pepe", "playerAlias": "A2", "objectType": "1"}, "19060518.4": {"playerId": "4", "playerName": "Dias", "playerAlias": "A3", "objectType": "1"}, "19060518.5": {"playerId": "5", "playerName": "Guerreiro", "playerAlias": "A4", "objectType": "1"}, "19060518.7": {"playerId": "7", "playerName": "Ronaldo", "playerAlias": "A5", "objectType": "1"}, "19060518.10": {"playerId": "10", "playerName": "Silva", "playerAlias": "A6", "objectType": "1"}, "19060518.14": {"playerId": "14", "playerName": "Carvalho", "playerAlias": "A7", "objectType": "1"}, "19060518.16": {"playerId": "16", "playerName": "Fernandes", "playerAlias": "A8", "objectType": "1"}, "19060518.18": {"playerId": "18", "playerName": "Neves", "playerAlias": "A9", "objectType": "1"}, "19060518.20": {"playerId": "20", "playerName": "Semedo", "playerAlias": "A10", "objectType": "1"}, "19060518.23": {"playerId": "23", "playerName": "Felix", "playerAlias": "A11", "objectType": "1"}, "19060518.101": {"playerId": "101", "playerName": "Sommer", "playerAlias": "B1", "objectType": "2"}, "19060518.102": {"playerId": "102", "playerName": "Mbabu", "playerAlias": "B2", "objectType": "2"}, "19060518.105": {"playerId": "105", "playerName": "Akanji", "playerAlias": "B3", "objectType": "2"}, "19060518.108": {"playerId": "108", "playerName": "Freuler", "playerAlias": "B4", "objectType": "2"}, "19060518.109": {"playerId": "109", "playerName": "Seferovic", "playerAlias": "B5", "objectType": "2"}, "19060518.110": {"playerId": "110", "playerName": "Xhaka", "playerAlias": "B6", "objectType": "2"}, "19060518.113": {"playerId": "113", "playerName": "Rodriguez", "playerAlias": "B7", "objectType": "2"}, "19060518.114": {"playerId": "114", "playerName": "Zuber", "playerAlias": "B8", "objectType": "2"}, "19060518.117": {"playerId": "117", "playerName": "Zakaria", "playerAlias": "B9", "objectType": "2"}, "19060518.122": {"playerId": "122", "playerName": "Schaer", "playerAlias": "B10", "objectType": "2"}, "19060518.123": {"playerId": "123", "playerName": "Shaqiri", "playerAlias": "B11", "objectType": "2"}}'

# # (True, properties in json format) -> if id found
# # (False, None) -> if not found
# def getListOfPropertiesOfItem(str_json, element):
#     json_str = json.loads(str_json)
#     if not json_str.get(element) == None:
#         #found
#         return((True, json_str.get(element)))
#     else:
#         #not found
#         return((False, None))

# print(getListOfPropertiesOfItem(text, '19060518.16')[1]['playerName'])


class GameState(faust.Record, serializer='json'):
    ts: str
    eventtype: str
    matchid: str
    description: str

test = GameState(ts='a', eventtype='b', matchid='c', description='e')


print(test)