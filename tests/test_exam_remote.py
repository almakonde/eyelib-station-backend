import requests

examination ={
    'morphology': {
            'chin_z': 1500.0, 
            'chin_to_eyeline': 125.0
            },
    'patient_name': 'Henry',
    'patient_id': 1
}



requests.put('http://127.0.0.1/examinations', json=examination)