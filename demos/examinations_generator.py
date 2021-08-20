import requests
import random
from time import sleep, time
from calendar import datetime

url = 'http://127.0.0.1:5003/examinations'
url_station_automation = 'http://127.0.0.1:5003/automation'
url_station_setup = 'http://127.0.0.1:5003/patient_adjust'

prefix_name = "DUMMY_TEST"

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

response = requests.put(url_station_automation, json={'command':'disable_patient_validation'})
station_setup_response = requests.get(url_station_setup)
station_setup = station_setup_response.json()

print(station_setup)
chin_z_tolerance = 10
chin_z_min = station_setup['chin_z_min'] + chin_z_tolerance
chin_z_max = station_setup['chin_z_max'] - chin_z_tolerance
chin_to_eyeline_min = station_setup['chin_to_eyeline_min']
chin_to_eyeline_max = station_setup['chin_to_eyeline_max']

index = 0

def random_date():
    random_number_of_days = random.randint(0,days_between_dates)
    random_date = start_date + datetime.timedelta(days=random_number_of_days)
    return str(random_date)

while True:
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

    patient = {'patient_name':prefix_name+' '+first_name+' '+last_name,
                'patient_id':index,
                'examination_id':index,
                'morphology':{'chin_z': chin_z, 'chin_to_eyeline': chin_to_eyeline},
                'instruments':['REVO', 'VX120'],
                'birth_date':random_date(),
                'gender': gender}

    print(patient)
    response = requests.put(url, json={'command':'examinations', 'data':patient})
    # sleep(random.randint(180,600)) # sleep entre 3 et 10 minutes
    sleep(random.randint(1,30)) # sleep entre 3 et 10 minutes