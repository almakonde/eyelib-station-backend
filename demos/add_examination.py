""""
This script sends a patient examination to station. 

Conditions: 
    The station shall be in gen2 automation mode.
Output:
    No instrument results are expected.
"""

import requests

station_ip = '10.1.1.1' # or localhost

patient_id = 1
first_name = 'TEST'
last_name = 'ABCD'
chin_z = 1400
chin_to_eyeline = 100
instruments = ['REVO', 'VX120'] # 'REVO' and/or 'VX120'
gender = 'Female' #'Female' or 'Male'
birth_date = '1959-10-30'


patient = {
        'patient_name':first_name+' '+last_name,
        'patient_id':patient_id,
        'examination_id':patient_id,
        'morphology':{'chin_z': chin_z, 'chin_to_eyeline': chin_to_eyeline},
        'instruments':instruments,
        'birth_date':birth_date,
        'gender': gender
    }
response = requests.put('http://'+station_ip+':5003/examinations', json={'command':'examinations', 'data':patient})

if response.status_code != requests.codes.ok:
    print('Something went wrong!')
else:
    print('Patient added succesfully!')