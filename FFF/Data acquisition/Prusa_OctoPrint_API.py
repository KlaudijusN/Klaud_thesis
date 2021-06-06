import requests
import json
import time
import sqlite3
import datetime

#Create and/or connect to the database
conn = sqlite3.connect('OctoPrint_API1.db')
### Makes SQLite code executable
c = conn.cursor()

#API KEY
headers = {
    'X-Api-Key': 'API Key',
}
#Local network IP adresss
IP_address = "XX.XXX.XX.XXX"

#API path 
printer_data = IP_address + '/api/printer'
display_layer_progress_data = IP_address + '/plugin/DisplayLayerProgress/values'
printer_job_data = IP_address +'/api/job'

#Time function
def time_():
    _ = datetime.datetime.now()
    return "%s" % _

#
def json_(api):
    data = requests.get(api, headers=headers).json()
    return data

def api_data():
    dict_ = {'Build_platform_temperature': json_(printer_data)['temperature']['bed']['actual'],
             'Build_platform_target_temperature': json_(printer_data)['temperature']['bed']['target'],
             'Hot_end_temperature' :json_(printer_data)['temperature']['tool0']['actual'],
             'Hot_end_temperature_target': json_(printer_data)['temperature']['tool0']['target'],
             'Progress': json_(printer_job_data)['progress']['completion'], #Percentage float in progress of completion
             'User': json_(printer_job_data)['job']['user'], #User 
             'Object_': json_(printer_job_data)['job']['file']['name'], #Gcode File name
             'Process_time': json_(printer_job_data)['progress']['printTime'], #Time in printing process (seconds)
             'Fan_speed': json_(display_layer_progress_data)['fanSpeed'],
            'Feed_rate': json_(display_layer_progress_data)['feedrate'],
            'Current_height': json_(display_layer_progress_data)['height']['current'],
            'Average_layer_duration': json_(display_layer_progress_data)['layer']['averageLayerDurationInSeconds'],
            'Last_layer_duration': json_(display_layer_progress_data)['layer']['lastLayerDurationInSeconds'],
            'Current_layer': json_(display_layer_progress_data)['layer']['current'],
            'Total_layers': json_(display_layer_progress_data)['layer']['total'],      
            'State':  json_(display_layer_progress_data)['print']['printerState'],
            'Date': time_()[:-7]
            }
    return dict_
    
    
###Function which posts to .db file
def post_row(conn, tablename, dict_):
    keys = ','.join(dict_.keys()) # Joins dictionary variables names with , seperated between.. so they are ordered like variable1, variable2,... etc
    question_marks = ','.join(list('?'*len(dict_))) ## creates question marks separates by comma according on how many varaibles, if 3 variables: '?,?,?'
    values = tuple(dict_.values()) #Converts dict_values into tuples format, i guess it is needed to avoid "dict_values([value1, value2,.. etc'])"
    conn.execute('INSERT INTO '+tablename+' ('+keys+') VALUES ('+question_marks+')', values)



# Function that creates SQLite table in database 
def create_table_API_data(table_name):
    dict_keys = list(api_data().keys())
    sql_table_var = [s +' TEXT' for s in dict_keys] #List comprehension, need to look more into it
    sql_table_var = ", ".join(sql_table_var)
    #conn.execute("CREATE TABLE IF NOT EXISTS OctoPrint_API_Data_TEST ({0})".format(sql_table_var))
    conn.execute("CREATE TABLE IF NOT EXISTS {0} ({1})".format(table_name,sql_table_var))
    
    
##Create SQLite table for API data and acquistion delays 
create_table_API_data('P_3')
c.execute('CREATE TABLE IF NOT EXISTS P_delays_3 (timetime number, timeperf_counter number, Date number)')

#Data acquistion while loop, which acquires and stores the data every second
while True:
    try :

        start_a = time.time()
        start_r = time.perf_counter()
        state = json_(display_layer_progress_data)['print']['printerState']

        
        if state == 'printing':

            post_row(conn, 'P_3', api_data())
            conn.commit() #This ensures that the row is actually posted 

            end_a = time.time()
            end_r = time.perf_counter()
            result_a = end_a - start_a
            result_r = end_r - start_r

            delays = {
                'timetime': result_a,
                'timeperf_counter': result_r,
                'Date': time_()
            }
            post_row(conn, 'P_delays_3', delays)
            conn.commit()
            time.sleep(1)
    except KeyboardInterrupt:
        print('\nStopped due to keyborard interrupt')
        break