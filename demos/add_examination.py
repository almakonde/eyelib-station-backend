""""
This script sends a patient examination to station. 

Conditions: 
    The station shall be in gen2 automation mode.
Output:
    No instrument results are expected.
"""

import requests

station_ip = 'localhost' # or 'localhost' or '10.1.1.1'

patient_id = 4
examination_id = 2
first_name = 'TEST'
last_name = 'ABCDE'
chin_z = 1522
chin_to_eyeline = 102
instruments = ['REVO', 'VX120'] # 'REVO' and/or 'VX120'
gender = 'Female' #'Female' or 'Male'
birth_date = '1959-02-15'


patient = {
        'patient_name':first_name+' '+last_name,
        'patient_id':patient_id,
        'examination_id':examination_id,
        'morphology':{'chin_z': chin_z, 'chin_to_eyeline': chin_to_eyeline},
        'instruments':instruments,
        'birth_date':birth_date,
        'gender': gender
    }
try: 
    response = requests.put('http://'+station_ip+':5003/examinations', json={'command':'examinations', 'data':patient})

    if response.status_code != requests.codes.ok:
        print('Something went wrong! Error code:%d', response.status_code)
    else:
        print('Patient added succesfully!')
except Exception as exception:
    print('Response exception: %s', str(exception))