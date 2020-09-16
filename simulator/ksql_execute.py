import requests, os
from requests.exceptions import HTTPError

#url_port_str : example : 'http://ksqldb-server-1:8088'
#ksql_command : example :  "INSERT INTO t_rawMetaPlayer (rowKey, gameId, sensorId, name, alias, objectType) VALUES ('19060518.1200', 19060518, 200 , 'Ball' , 'BALL' , 0);"
#strings have to be marked with the ' char
def ksqlCommandExecute(url_port_str, ksql_command):
    try:
        #response = requests.get(
        response = requests.post(
            url_port_str+'/ksql',
            headers={"Accept": "application/vnd.ksql.v1+json", "Content-Type": "application/vnd.ksql.v1+json"},
            data='{"ksql":"'+str(ksql_command.replace("'", "\'"))+'"}',
            timeout=1.5,
        )   

        #response = requests.get(url)
        # If the response was successful, no Exception will be raised
        response.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')  # Python 3.6
    except Exception as err:
        print(f'Other error occurred: {err}')  # Python 3.6
    else:
        print('Success!')
        return(response)

url_port = 'http://ksqldb-server-1:8088'
#command = "INSERT INTO t_rawMetaPlayer (rowKey, gameId, sensorId, name, alias, objectType) VALUES ('19060518.1200', 19060518, 200 , 'Ball' , 'BALL' , 0);"

# Open game JSON file
with open(os.path.join(os.getcwd(), 'initKafkaTopics.sql')) as file: 
    ksql_commands = file.readlines() 
ksql_commands = [line.strip() for line in ksql_commands if (line.find('--') == -1) and (len(line.strip()) != 0)] 

for ksql_command in ksql_commands:
    print(ksql_command)
    print(ksqlCommandExecute(url_port_str=url_port, ksql_command=ksql_command))
    #break