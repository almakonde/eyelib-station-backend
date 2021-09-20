import requests
from pprint import pprint as pp

def add_patients(patients, url, exs):
    for patient in patients:
        resp = requests.put(url, json={'command':'examinations', 'data': exs.factory(**patient)})

title_bar = lambda title='', rep=64: f' {title} '.rjust(1+rep//2 + len(title)//2, '=').ljust(rep, '=')
box = lambda text, title='', prefix='', rep=64: f'\n{rep*"=" if not title else title_bar(title, rep)}\n{prefix}{text}\n{rep*"="}\n'

class TestExaminations:
    def test_examination_add(self, server_examinations, patients):
        _, url, exs = server_examinations

        for patient in patients:
            resp = requests.put(url, json={'command': 'examinations', 'data': exs.factory(**patient)})
            print(box(resp))
            if resp is not None and resp.ok:
                print(box(resp.json(), prefix='Result: '))
                assert resp.json().get('ret', False)

        pool = exs.get()
        print(box(pool, f'test_add POOL (exs.get)'))
        new_patients = [{k: v for k, v in patient[1].items() if k.startswith('patient')} for patient in pool.items()]
        assert new_patients == patients

    def test_examination_get(self, server_examinations, patients):
        _, url, exs = server_examinations

        add_patients(patients, url, exs)
        
        resp = requests.get(url)
        print(box(resp.json(), f'test_get RESP json (resp.json())'))
        print(box(resp.text, f'test_get RESP text (resp.text)'))
        new_patients = [{k: v for k, v in patient[1].items() if k.startswith('patient')} for patient in resp.json().items()]

        assert new_patients == patients
    
    def test_examination_delete(self, server_examinations, patients):
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
        print(box(new_patients2))
        print(box(remaining_patients))

        assert new_patients1 == patients
        assert new_patients2 == remaining_patients

    
    def test_examination_get_config(self, server_examinations):
        _, url, exs = server_examinations
        resp = requests.get(url, json={'command': 'config'})

        assert resp is not None
        assert 'auto_pick' in resp.json()
        pp(box(resp.json(), 'test_get_config', 'resp: '))

    def test_examination_get_sparse(self, server_examinations, patients):
        _, url, exs = server_examinations

        add_patients(patients, url, exs)

        resp1 = requests.get(url, json={'command': 'item', 'data': 1})
        resp2 = requests.get(url, json={'command': 'item', 'data': [1, 2]})
        assert resp1 is not None
        assert resp1.json()['examination_id'] == 1

        sparse = resp2.json()
        assert len(sparse) == 2
        assert sparse[0]['examination_id'] == 1
        assert sparse[1]['examination_id'] == 2


    def test_examination_set_config(self, server_examinations):
        _, url, exs = server_examinations

        config = exs.get_config()
        assert config['auto_pick']
        
        resp = requests.put(url, json={'command': 'config', 'data': {'auto_pick': False}})
        config = exs.get_config()
        assert not config['auto_pick']

