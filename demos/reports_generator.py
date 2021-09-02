import requests

""""
This script generates all the reports for patient IDs inside the patient_ids.txt.

Output:
    The report pdf files are saved in the current folder.
"""

manager_ip = '10.1.0.2'
manager_port = '5003'
manager_address = 'http://' + manager_ip + ':' + manager_port + '/'
patient_ids_file = 'patients_ids.txt'


with open(patient_ids_file,'r') as ids_reader:
    for id_str in ids_reader.readlines():
        try:
            id = int(id_str)        
        except ValueError:
            print("That was not a valid number. It might be the end of the file.")
            continue
        
        print(f'Start reporting for patient {id}')
        res = requests.get(f'{manager_address}generateReport?patientId={id}')
        if res.ok:
            print(f'Done reporting for patient {id}')
            with open(res.headers['X-Suggested-Filename'], 'wb') as pdf_writer:
                pdf_writer.write(res.content)
                print(f'Saved pdf for patient {id}')
        else:
            print(f'Not a valid request for patient {id}')