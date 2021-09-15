import requests

def add_patients(patients, url, exs):
    for patient in patients:
        resp = requests.put(url, json={'command':'examinations', 'data': exs.factory(**patient)})


class TestExaminations:
    
    def test_start(self, requests_server):
        server, _, _ = requests_server
        server.start()
        assert server.is_running()
        server.shutdown()
        server.join()
        assert not server.is_running()
    
    def test_add(self, requests_server, patients):
        server, url, exs = requests_server
        server.start()

        for patient in patients:
            resp = requests.put(url, json={'command': 'examinations', 'data': exs.factory(**patient)})
            if resp is not None:
                print(f'\n{32*"="}\nResult: {resp}\n{32*"="}\n')
                # print(f'\n{32*"="}\nResult: {resp.json()}\n{32*"="}\n')
                assert resp.json().get('ret', False)

        server.shutdown()
        server.join()

        pool = exs.get()
        assert len(pool) == 4

    def A_test_get(self, requests_server, patients):
        server, url, exs = requests_server
        server.start()

        add_patients(patients, url, exs)
        
        resp = requests.get(url)

        server.shutdown()
        server.join()

        assert len(resp.json()) == 4
    
    def A_test_delete(self, requests_server, patients):
        server, url, exs = requests_server
        server.start()

        add_patients(patients, url, exs)
        
        resp1 = requests.get(url)

        requests.delete(url, json={'item':{'examination_id':1}})
        requests.delete(url, json={'item':{'examination_id':3}})
        
        resp2 = requests.get(url)

        server.shutdown()
        server.join()

        assert len(resp1.json()) == 4
        assert len(resp2.json()) == 2

        assert str(2) in resp2.json().keys()
        assert str(4) in resp2.json().keys()
        assert str(1) not in resp2.json().keys()
        assert str(3) not in resp2.json().keys()
    
    def A_test_get_config(self, requests_server):
        server, url, exs = requests_server
        server.start()
        resp = requests.get(url, json={'command': 'config'})

        server.shutdown()
        server.join()

        assert resp is not None
        assert 'auto_pick' in resp.json()

    def A_test_get_sparse(self, requests_server, patients):
        server, url, exs = requests_server
        server.start()

        add_patients(patients, url, exs)

        resp1 = requests.get(url, json={'command': 'item', 'data': 1})
        resp2 = requests.get(url, json={'command': 'item', 'data': [1, 2]})

        server.shutdown()
        server.join()

        assert resp1 is not None
        assert resp1.json()['examination_id'] == 1

        sparse = resp2.json()
        assert len(sparse) == 2
        assert sparse[0]['examination_id'] == 1
        assert sparse[1]['examination_id'] == 2


    def A_test_set_config(self, requests_server):
        server, url, exs = requests_server
        server.start()

        config = exs.get_config()
        assert config['auto_pick']
        
        resp = requests.put(url, json={'command': 'config', 'data': {'auto_pick': False}})
        config = exs.get_config()
        assert not config['auto_pick']

        server.shutdown()
        server.join()
