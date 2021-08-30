import requests
import random
from time import sleep
from calendar import datetime
import logging

""""
This script generates random patients and push them to manager. 
The manager sends them to the station.

Conditions: 
    The station shall be in gen2 automation mode.
    The VX and REVO instruments shall be apriori set up to work with dummy eyes.
Output:
    At the end of each examination, the results from instruments should be found in the manager.
"""

logging.basicConfig(filename='examinations_generator.log', format='%(asctime)s %(message)s', level=logging.INFO)

number_of_patients_to_generate = 100
patient_arrival_range_in_min = (3, 10)

# end points declarations
station_ip = '10.1.1.1'
station_port = '5003'
station_address = 'http://' + station_ip + ':' + station_port + '/'

manager_ip = '10.1.0.2'
manager_port = '5003'
manager_address = 'http://' + manager_ip + ':' + manager_port + '/'

station_automation_url = station_address + 'automation'
station_setup_url = station_address + 'patient_adjust'

manager_patient_registration_url = manager_address + 'registerPatient'
manager_morphology_registration_url = manager_address + 'registerMorphology'
manager_patient_to_station_url = manager_address + 'pushToStation'

logging.info("Start examinations_generator")
logging.info("station_address=%s",station_address)
logging.info("manager_address=%s",manager_address)
logging.info("number_of_patients_to_generate=%d",number_of_patients_to_generate)
logging.info("patient_arrival (min, max) =(%d, %d) minutes",patient_arrival_range_in_min[0],patient_arrival_range_in_min[1])

# input data for creating a random patient
prefix_name = "DUMMY"

females = ("Mary","Elizabeth","Patricia","Jennifer","Linda","Barbara","Margaret","Susan","Dorothy","Sarah",
            "Jessica","Helen","Nancy","Betty","Karen","Lisa","Anna","Sandra","Emily","Ashley",
            "Kimberly","Donna","Ruth","Carol","Michelle","Laura","Amanda","Melissa","Rebecca","Deborah",
            "Stephanie","Sharon","Kathleen","Cynthia","Amy","Shirley","Emma","Angela","Catherine","Virginia",
            "Katherine","Brenda","Pamela","Frances","Nicole","Christine","Samantha","Evelyn","Rachel","Alice")
males = ("James","John","Robert","Michael","William","David","Joseph","Richard","Charles","Thomas",
            "Christopher","Daniel","Matthew","George","Anthony","Donald","Paul","Mark","Andrew","Edward",
            "Steven","Kenneth","Joshua","Kevin","Brian","Ronald","Timothy","Jason","Jeffrey","Ryan",
            "Jacob","Frank","Gary","Nicholas","Eric","Stephen","Jonathan","Larry","Justin","Raymond","Scott",
            "Samuel","Brandon","Benjamin","Gregory","Jack","Henry","Patrick","Alexander","Walter")
surnames = ("SMITH	","JOHNSON","WILLIAMS","JONES","BROWN","DAVIS","MILLER","WILSON","MOORE","TAYLOR",
            "ANDERSON","THOMAS","JACKSON","WHITE","HARRIS","MARTIN","THOMPSON","GARCIA","MARTINEZ","ROBINSON",
            "CLARK","RODRIGUEZ","LEWIS","LEE","WALKER","HALL","ALLEN","YOUNG","HERNANDEZ","KING",
            "WRIGHT","LOPEZ","HILL","SCOTT","GREEN","ADAMS","BAKER","GONZALEZ","NELSON","CARTER",
            "MITCHELL","PEREZ","ROBERTS","TURNER","PHILLIPS","CAMPBELL","PARKER","EVANS","EDWARDS","COLLINS")
start_date = datetime.date(1920, 1, 1)
end_date = datetime.date(2020, 12, 31)
time_between_dates = end_date - start_date
days_between_dates = time_between_dates.days

def random_date():
    random_number_of_days = random.randint(0,days_between_dates)
    random_date = start_date + datetime.timedelta(days=random_number_of_days)
    return str(random_date)

# get program name and print it in the log file
automation_response = requests.get(station_automation_url)
program = automation_response.json().get('program')
logging.info("program: %s",program)
if program != 'gen2':
    logging.warning('gen2 is not the current program. current = %s', program)

# disable patient validation (i.e.: do not wait for patient departure because the dummy head is always present)
automation_response = requests.put(station_automation_url, json={'command':'disable_patient_validation'})
if automation_response.status_code != requests.codes.ok:
    logging.error('Exit. disable_patient_validation request failure with code %d', automation_response.status_code)
    exit()
# get station settings
station_setup_response = requests.get(station_setup_url)
station_setup = station_setup_response.json()

chin_z_tolerance = 10
chin_z_min = int(station_setup['chin_z_min'] + chin_z_tolerance)
chin_z_max = int(station_setup['chin_z_max'] - chin_z_tolerance)
chin_to_eyeline_min = int(station_setup['chin_to_eyeline_min'])
chin_to_eyeline_max = int(station_setup['chin_to_eyeline_max'])

logging.info("birthdate: start_date=%s end_date=%s",str(start_date),str(end_date))
logging.info("morpho: chin_z_min=%d chin_z_max=%d chin_to_eyeline_min=%d chin_to_eyeline_max=%d",
        chin_z_min, chin_z_max, chin_to_eyeline_min, chin_to_eyeline_max)


index = 0
while index < number_of_patients_to_generate:
    # creating a random patient
    index = index + 1
    gender_flag = bool(random.getrandbits(1))  
    if gender_flag:
        gender = "Male"
        first_name = males[random.randint(0, len(males) - 1)]
    else:
        gender = "Female"
        first_name = females[random.randint(0, len(females) - 1)]
    last_name = surnames[random.randint(0, len(surnames) - 1)]

    chin_z = random.randint(chin_z_min, chin_z_max)
    chin_to_eyeline = random.randint(chin_to_eyeline_min, chin_to_eyeline_max)

    # register a patient and get the patient ID
    patient_data = {
                'firstName': prefix_name+' '+first_name,
                'surname': last_name,
                'gender': int(gender_flag),
                'birthDate': random_date()
            }
    response = requests.post(manager_patient_registration_url, json=patient_data)
    if response.status_code != requests.codes.ok:
        logging.error('patient request failure with code %d', response.status_code)
        break
    patient_id = response.json()

    # register patient morphology
    morpho_data = {
                'chin2Eyes': chin_to_eyeline,
                'chin2Floor': chin_z
            }
    _ = requests.post(manager_morphology_registration_url, json=morpho_data)
    logging.info('index=%d patient_id=%d patient_data=%s morpho_data=%s', index, patient_id, patient_data, morpho_data)

    # send patient to station
    _ = requests.post(manager_patient_to_station_url, json={
                'patientId': patient_id
            })

    # use in simulation
    # patient = {'patient_name':prefix_name+' '+first_name+' '+last_name,
    #             'patient_id':index,
    #             'examination_id':index,
    #             'morphology':{'chin_z': chin_z, 'chin_to_eyeline': chin_to_eyeline},
    #             'instruments':['REVO', 'VX120'],
    #             'birth_date':random_date(),
    #             'gender': gender}
    # response = requests.put(station_address + 'examinations', json={'command':'examinations', 'data':patient})

    sleep(random.randint(patient_arrival_range_in_min[0]*60, patient_arrival_range_in_min[1]*60)) # sleep entre 3 et 10 minutes

logging.info("End examinations_generator")