from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
import datetime
import sqlite3
import time
from login import driver

### Function which posts to .db file
def post_row(conn, tablename, dict_):
    keys = ','.join(dict_.keys()) # Joins dictionary variables names with , seperated between.. so they are ordered like variable1, variable2,... etc
    question_marks = ','.join(list('?'*len(dict_))) ## creates question marks separates by comma according on how many varaibles, if 3 variables: '?,?,?'
    values = tuple(dict_.values()) #Converts dict_values into tuples format, i guess it is needed to avoid "dict_values([value1, value2,.. etc'])"
    conn.execute('INSERT INTO '+tablename+' ('+keys+') VALUES ('+question_marks+')', values)
    

### Date & Time function
def time_():
    _ = datetime.datetime.now()
    return "%s" % _ 

### Class for calling CSS selector
class CSS_Selector:
    def __init__(self, CSS):
        self.CSS = CSS
    def data(self):
        return driver.find_element_by_css_selector('{}'.format(self.CSS)).text
    
### function for cleaning some values such as (27C = 27)
def data_sorted(x):
    if x == "plastic_t":
        return plastic_t.data().split("°")[0]
    elif x == "fiber_t":
        return fiber_t.data().split("°")[0]
    elif x == "time_l":
        return time_l.data().split("m")[0]
    elif x == "current_layer":
        return int(layer.data().split("of")[0]) 
    elif x == "total_layers":
        return int(layer.data().split("of")[1])
    else:
        pass
    
    

#Create and/or connect to the database
conn = sqlite3.connect('Markforged_Data.db')
### Makes SQLite code executable
c = conn.cursor() 

### Tables for FFF printer data during printing and other states
c.execute('CREATE TABLE IF NOT EXISTS "M_9" (Plastic_Temperature number, Fiber_Temperature number, Machine_state text, Date number, Current_Layer number, Total_Layers number, Printed_Object, User text, Time_left number, Plastic_material text )')
###                   Tables for delays 
c.execute('CREATE TABLE IF NOT EXISTS "Delays_9" (timetime number, timeperf_counter number, Date number)')


### Static variables 
plastic_t = CSS_Selector('#library > div:nth-child(2) > div.device-detail-info.status-section-detail.ng-scope > div:nth-child(1) > div.form-table-cell.large-text.ng-binding')
fiber_t = CSS_Selector('#library > div:nth-child(2) > div.device-detail-info.status-section-detail.ng-scope > div.form-table-row.tooltip-visibility-target.ng-scope > div.form-table-cell.large-text.ng-binding')
status = CSS_Selector("div[ng-class='$ctrl.getClassStatus()']") 
layer = CSS_Selector('#library > div:nth-child(2) > div:nth-child(3) > div > span:nth-child(3) > div')
object_ = CSS_Selector('#current-print-link')
user = CSS_Selector('#library > div:nth-child(2) > div:nth-child(3) > div > span:nth-child(2) > div')
time_l = CSS_Selector('#library > div:nth-child(1) > div.device-detail > div > div.form-flex-container.flex-direction-column > div.device-detail-column-lower > div.device-detail-row > div.time-left.ng-binding')
plastic_m = CSS_Selector('#library > div:nth-child(2) > div.device-detail-info.status-section-detail.ng-scope > div:nth-child(1) > div:nth-child(4) > div')

### Acquisition time
sleep_printing = 1

#Data acquistion while loop, which acquires and stores the data every second
while True:
    try:
        state = status.data()
        start_a = time.time()
        start_r = time.perf_counter()
        if state == "Printing":
            data_printing = {
            'Plastic_Temperature': data_sorted("plastic_t"),
            'Fiber_Temperature': data_sorted("fiber_t"),
            'Current_Layer': data_sorted("current_layer"),
            'Total_Layers': data_sorted("total_layers"),
            'Printed_Object': object_.data(),
            'Machine_state': status.data(),
            'User': user.data(),
            'Date': time_()[:-7],
            'Time_left': data_sorted("time_l"),
            'Plastic_material': plastic_m.data()
            }

            post_row(conn, 'M_9', data_printing) #post the row in SQLite table
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
            post_row(conn, 'Delays_9', delays)
            conn.commit()
            time.sleep(sleep_printing)
    except KeyboardInterrupt:
            print('\nStopped due to keyborard interrupt')
            break

