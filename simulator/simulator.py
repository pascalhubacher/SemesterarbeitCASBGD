#
import time
import math
import os
import itertools
import json
from multiprocessing import Pool

# Globals
# JSON keys
STR_PATH = 'path'
STR_CONFIG_PROPERTIES = 'config.properties'
STR_NUMBER_OF_ELEMENTS = 'number_of_elements'
STR_WORK = 'work'
LST_NOT_ELEMENT = [STR_NUMBER_OF_ELEMENTS]
STR_HOME = 'home'
STR_AWAY = 'away'
STR_BALL = 'ball'
STR_OTHER = 'other'
#time laps
INT_TIME_LAPS = 1

def execute_log_data(data_log):
    print(' Process player id {} team ({}) started'.format(data_log[0], data_log[1]))
    with open(data_log[2]) as f:
        lines = f.readlines()

    time_elapsed = 0
    i = 0
    for line in lines[1:]: 
        i += 1
        if i <= 500:
            #print(line.strip())
            #40ms -> 40/1000 -> 0.04s
            #the time in the log is cummulated so the last time vales is subtracted each time to get the delta time
            #the time value is divided by the time laps factor which can be set at each run (INT_TIME_LAPS)
            time.sleep((int(line.strip().split(',')[0])- time_elapsed)/1000/INT_TIME_LAPS)
            #the last time value
            time_elapsed = int(line.strip().split(',')[0])
        
        #do something

    print(' Process player id {} team ({}) finished'.format(data_log[0], data_log[1]))

#create json structure out of the data
def create_data_json(filepath):
    #get all filepaths to all files
    dct_data = {}
    number_of_elements = 0
    dct_data[STR_HOME] = {}
    dct_data[STR_AWAY] = {}
    dct_data[STR_BALL] = {}
    dct_data[STR_OTHER] = {}

    # tuple of all the (player_id, home/away/ball, path)
    tpl_work = ()
 
    walker = os.walk(filepath)
    for root, _dirs, files in walker:
       for file_ in files:
            path = os.path.join(root, file_)

            player_id = str(get_player_id(path))

            if STR_HOME in path:
                dct_data[STR_HOME][player_id] =  {}
                dct_data[STR_HOME][player_id][STR_PATH] = path

                tpl_work += ([player_id, STR_HOME, path],)

                if dct_data[STR_HOME].get(STR_NUMBER_OF_ELEMENTS) == None:
                    dct_data[STR_HOME][STR_NUMBER_OF_ELEMENTS] = 1
                else:
                    dct_data[STR_HOME][STR_NUMBER_OF_ELEMENTS] = int(dct_data[STR_HOME][STR_NUMBER_OF_ELEMENTS]) + 1
                
                number_of_elements += 1
            elif STR_CONFIG_PROPERTIES in path:
                dct_data[STR_CONFIG_PROPERTIES] = path

            elif STR_AWAY in path:
                dct_data[STR_AWAY][player_id] =  {}
                dct_data[STR_AWAY][player_id][STR_PATH] = path

                tpl_work += ([player_id, STR_AWAY, path],)
                
                if dct_data[STR_AWAY].get(STR_NUMBER_OF_ELEMENTS) == None:
                    dct_data[STR_AWAY][STR_NUMBER_OF_ELEMENTS] = 1
                else:
                    dct_data[STR_AWAY][STR_NUMBER_OF_ELEMENTS] = int(dct_data[STR_AWAY][STR_NUMBER_OF_ELEMENTS]) + 1
                
                number_of_elements += 1
            elif STR_BALL in path:
                dct_data[STR_BALL][player_id] =  {}
                dct_data[STR_BALL][player_id][STR_PATH] = path
                
                tpl_work += ([player_id, STR_BALL, path],)

                if dct_data[STR_BALL].get(STR_NUMBER_OF_ELEMENTS) == None:
                    dct_data[STR_BALL][STR_NUMBER_OF_ELEMENTS] = 1
                else:
                    dct_data[STR_BALL][STR_NUMBER_OF_ELEMENTS] = int(dct_data[STR_BALL][STR_NUMBER_OF_ELEMENTS]) + 1
                
                number_of_elements += 1
            else:
                dct_data[STR_OTHER][player_id] =  {}
                dct_data[STR_OTHER][player_id][STR_PATH] = path
                
                if dct_data[STR_OTHER].get(STR_NUMBER_OF_ELEMENTS) == None:
                    dct_data[STR_OTHER][STR_NUMBER_OF_ELEMENTS] = 1
                else:
                    dct_data[STR_OTHER][STR_NUMBER_OF_ELEMENTS] = int(dct_data[STR_OTHER][STR_NUMBER_OF_ELEMENTS]) + 1
                
                number_of_elements += 1
            
    dct_data[STR_NUMBER_OF_ELEMENTS] = number_of_elements
    dct_data[STR_WORK] = tpl_work
    return(dct_data)

# get the player id back from the filename
# 1.csv -> player id = 1
def get_player_id(str_filepath, str_suffix='.csv'):
    return(str_filepath[str_filepath.rfind('\\')+1:-len(str_suffix)])
    
def main():
    start_time = time.perf_counter()
    
    print('{} - Preparing data - start'.format(time.perf_counter()))
    
    #create json object out of the files
    # '..' -> one folder up
    dct_data = create_data_json(os.path.join(os.path.dirname( __file__ ), 'data'))
    #write to file
    #with open(os.path.join(os.getcwd(), 'game.json'), 'w') as outfile:
    #    json.dump(dct_data, outfile)

    #what to do in a list
    #key: 'work'     
    # #[0] ["7", "home", "C:\\Users\\pasca\\HV\\github\\SemesterarbeitCASBGD\\data\\home\\7.csv"]
    work = dct_data[STR_WORK]

    print('{} - Preparing data - end'.format(time.perf_counter()))

    start_time = time.perf_counter()
    print('{} - Starting to send data in parallel - start'.format(time.perf_counter()))

    # 2 x 11 players and the ball -> 23
    num_processes = int(dct_data[STR_NUMBER_OF_ELEMENTS])
    #num_processes = 1

    with Pool(processes=num_processes) as pool:
        pool.map(execute_log_data, work)
    
    print('{} - Starting to send data in parallel - end'.format(time.perf_counter()))

    end_time = time.perf_counter()
    print(start_time, end_time)
    print('{} - Took: {} s'.format(time.perf_counter(), end_time - start_time))

if __name__ == "__main__":
    main()