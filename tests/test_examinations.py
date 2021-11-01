import requests

from tests.utils import *

def add_patients(patients, url, exs):
    success = 0
    failed = 0
    for patient in patients:
        resp = requests.put(url, json={'command':'examinations', 'data': exs.factory(**patient)})
        success += resp.ok
        failed += not resp.ok
        print(box(resp.status_code, f'add_patients: {patient}', prefix='Result: '))
    return success, failed


class TestExaminations:
    def test_examination_add_patients(self, server_examinations, patients):
        _, url, exs = server_examinations

        for patient in patients:
            resp = requests.put(url, json={'command': 'examinations', 'data': exs.factory(**patient)})
            if resp is not None and resp.ok:
                print(fox(resp.json(), 'test_examination_add_patients', prefix='Result: '))
                assert resp.json().get('ret', False)

        pool = exs.get()
        print(fox(pool, f'test_add POOL (exs.get)'))
        new_patients = [{k: v for k, v in patient[1].items() if k.startswith('patient')} for patient in pool.items()]
        assert new_patients == patients

    def test_examination_get_patients(self, server_examinations, patients):
        _, url, exs = server_examinations
        new_patients = []

        success, failed = add_patients(patients, url, exs)
        assert success == len(patients)
        assert failed == 0
        resp = requests.get(url)
        if resp is not None and resp.ok:
            print(fox(resp.json(), f'test_examination_get_patients RESP json (resp.json())'))
            new_patients = [{k: v for k, v in patient[1].items() if k.startswith('patient')} for patient in resp.json().items()]

        assert new_patients == patients
    
    def test_examination_delete_patients(self, server_examinations, patients):
        _, url, exs = server_examinations

        add_patients(patients, url, exs)
        deletes = [1, 3]
        remaining_patients = [patient for patient in patients if patient['patient_id'] not in deletes]
        
        resp1 = requests.get(url)
        new_patients1 = [{k: v for k, v in patient[1].items() if k.startswith('patient')} for patient in resp1.json().items()]

        for delete in deletes:
            requests.delete(url, json={'item': {'examination_id': delete}})
        
        resp2 = requests.get(url)
        new_patients2 = [{k: v for k, v in patient[1].items() if k.startswith('patient')} for patient in resp2.json().items()]
        print(fox(new_patients2, 'test_examination_delete_patients', 'Should delete:\n'))
        print(fox(remaining_patients, 'test_examination_delete_patients', 'Deleted:\n'))

        assert new_patients1 == patients
        assert new_patients2 == remaining_patients

    def test_examination_get_config(self, server_examinations):
        _, url, exs = server_examinations
        resp = requests.get(url, json={'command': 'config'})
        if resp is not None and resp.ok:
            print(fox(resp.json(), 'test_examination_get_config'))
            assert resp is not None
            assert 'auto_pick' in resp.json()
        else:
            assert resp.ok

    def test_examination_get_sparse(self, server_examinations, patients):
        _, url, exs = server_examinations

        add_patients(patients, url, exs)

        resp1 = requests.get(url, json={'command': 'item', 'data': 1})
        resp2 = requests.get(url, json={'command': 'item', 'data': [1, 2]})
        print(fox(resp1.json(), 'test_examination_get_sparse', 'Data = 1:\n'))
        assert resp1 is not None
        assert resp1.json()['examination_id'] == 1

        sparse = resp2.json()
        print(fox(sparse, 'test_examination_get_sparse', 'Sparse (data = [1, 2]):\n'))
        assert len(sparse) == 2
        assert sparse[0]['examination_id'] == 1
        assert sparse[1]['examination_id'] == 2

    def test_examination_set_config(self, server_examinations):
        _, url, exs = server_examinations

        config = exs.get_config()
        print(fox(config, 'test_examination_set_config', 'Before:\n'))
        assert config['auto_pick']
        
        resp = requests.put(url, json={'command': 'config', 'data': {'auto_pick': False}})
        config = exs.get_config()
        print(fox(config, 'test_examination_set_config', 'After:\n'))
        assert not config['auto_pick']

