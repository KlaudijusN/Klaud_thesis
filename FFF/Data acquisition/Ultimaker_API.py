import requests
import json
import time
import sqlite3
import datetime

#Create/Connect to the database
conn = sqlite3.connect('Ultimaker_API.db')
c = conn.cursor()

rest = "http://"
#Local network IP adresss
ip = "XX.XXX.XX.XXX" 
start_url = rest+ip

#Ultimaker Relative path 
docs_api = start_url + "/docs/api/"
url = rest+ip+docs_api


### API's of data variables

bed_t_now = start_url+ "/api/v1/printer/bed/temperature/current"
bed_t_target = start_url+"/api/v1/printer/bed/temperature/target"
tool1_t = start_url +'/api/v1/printer/heads/0/extruders/1/hotend/temperature/current'
tool1_target = start_url+'/api/v1/printer/heads/0/extruders/1/hotend/temperature/target'
tool1_fan = start_url + "/api/v1/printer/heads/0/fan"
position = start_url + "/api/v1/printer/heads/0/position"
head_acceleration = start_url +"/api/v1/printer/heads/0/acceleration"
acceleration = start_url + "/api/v1/printer/heads/0/extruders/1/feeder/acceleration"
jerk = start_url + "/api/v1/printer/heads/0/extruders/1/feeder/jerk"
max_speed = start_url + "/api/v1/printer/heads/0/extruders/1/feeder/max_speed"
z_offset = start_url + "/api/v1/printer/heads/0/extruders/1/hotend/offset/z" 
hotend1_material_extruded = start_url + "/api/v1/printer/heads/0/extruders/1/hotend/statistics/material_extruded"
hotend1_max_temperature_exposed = start_url + "/api/v1/printer/heads/0/extruders/1/hotend/statistics/max_temperature_exposed"
hotend1_time_spent_hot = start_url + "/api/v1/printer/heads/0/extruders/1/hotend/statistics/time_spent_hot"
status = start_url+'/api/v1/printer/status'
progress = start_url+ "/api/v1/print_job/progress"
name = start_url+ "/api/v1/print_job/name"
estimated_time = start_url+ "/api/v1/print_job/time_total"

#Time function
def time_():
    _ = datetime.datetime.now()
    return "%s" % _

### Requests API to JSON format
def json_(api):
    data = requests.get(api).json()
    return data

def api_data():
    dict_ = {'Build_platform_temperature': json_(bed_t_now),
            'Build_platform_target_temperature': json_(bed_t_target),
            'Hot_end1_temperature': json_(tool1_t),
            'Hot_end1_target_temperature': json_(tool1_target),
            'Hot_end1_fan': json_(tool1_fan),
            'Head_acceleration':json_(head_acceleration),
             

            'Feeder_acceleration': json_(acceleration),
            'Feeder_jerk': json_(jerk),
            'Feeder_max_speed': json_(max_speed),

            'Z_offset': json_(z_offset),
            'X_coordinate': json_(position)['x'],
            'Y_coordinate': json_(position)['y'],
            'Z_coordinate': json_(position)['z'],
            'Hot_end1_material_extruded': json_(hotend1_material_extruded),
            'Hot_end1_max_temperature_exposed':json_(hotend1_max_temperature_exposed),
            'Hot_end1_time_spent_hot': json_(hotend1_time_spent_hot),
            'Status': json_(status),
            'Progress': json_(progress),
            'Object': json_(name), 
            'Date': time_()[:-7]}
    return dict_

###Function which posts to .db file
def post_row(conn, tablename, dict_):
    keys = ','.join(dict_.keys()) # Joins dictionary variables names with , seperated between.. so they are ordered like variable1, variable2,... etc
    question_marks = ','.join(list('?'*len(dict_))) ## creates question marks separates by comma according on how many varaibles, if 3 variables: '?,?,?'
    values = tuple(dict_.values()) #Converts dict_values into tuples format, i guess it is needed to avoid "dict_values([value1, value2,.. etc'])"
    conn.execute('INSERT INTO '+tablename+' ('+keys+') VALUES ('+question_marks+')', values)


### Function for creating table in sqlite 
# This function is only working for string values due to "TEXT" or else it would be something else
def create_table(table_name):
    dict_keys = list(api_data().keys())
    sql_table_var = [s +' TEXT' for s in dict_keys] #List comprehension, need to look more into it
    sql_table_var = ", ".join(sql_table_var)
    conn.execute("CREATE TABLE IF NOT EXISTS {0} ({1})".format(table_name,sql_table_var))


###Converts both keys and values into strings, this is due to create_table()   
def dict_string():
    dict_ = api_data()
    keys_values = dict_.items()
    dict_str = {str(key): str(value) for key, value in keys_values}
    return dict_str

### Creates table with name set name
create_table('U_4')
c.execute('CREATE TABLE IF NOT EXISTS U_delays_4 (timetime number, timeperf_counter number, Date number)')

#Data acquistion while loop, which acquires and stores the data every second
while True:
    try:
        start_a = time.time()
        start_r = time.perf_counter()
        state = json_(status)
        B_t_target = json_(bed_t_target)
        if state == "printing" and B_t_target >0 : #To avoid false positives after priting is complete Alternatively you can use progress aswelll
            post_row(conn, 'U_4', dict_string())
            conn.commit()
            end_a = time.time()
            end_r = time.perf_counter()
            result_a = end_a - start_a
            result_r = end_r - start_r

            delays = {
                'timetime': result_a,
                'timeperf_counter': result_r,
                'Date': time_()[:-7]
            }
            post_row(conn, 'U_delays_4', delays)
            conn.commit()
            time.sleep(1)
    except KeyboardInterrupt:
        print('\nStopped due to keyborard interrupt')
        break

