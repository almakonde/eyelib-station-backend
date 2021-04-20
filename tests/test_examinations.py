import unittest
from station_backend.views.examinations import Examinations, ExaminationsView
from mjk_backend.threaded_server import ThreadedServer
import threading
import requests
import queue
import time

from flask import Flask

app = Flask("test_examination")

server = ThreadedServer(app, 'test')

url = 'http://127.0.0.1:5000/examinations'

exs = Examinations()

patients = [
    {'patient_name': 'Henry', 'patient_id':1},
    {'patient_name': 'Paul', 'patient_id':2},
    {'patient_name': 'John', 'patient_id':3},
    {'patient_name': 'Ringo', 'patient_id':4}
]

def add_patients():
    for i in range(0, 4):
        resp = requests.put(url, json={'command':'examinations', 'data': exs.factory(**patients[i])})


class TestExaminations(unittest.TestCase):
    
    def test_start(self):
        ex = ExaminationsView(app, exs)
        server.start()
        self.assertTrue(server.is_running())       
        server.shutdown()
        server.join()
        self.assertFalse(server.is_running())
    
    def test_add(self):
        ex = ExaminationsView(app, exs)
        server.start()

        for i in range(0, 4):
            resp = requests.put(url, json={'command': 'examinations', 'data': exs.factory(**patients[i])})
            if resp is not None:
                self.assertTrue(resp.json().get('ret', False))

        pool = exs.get()
        self.assertEqual(len(pool), 4)

        server.shutdown()
        server.join()

    def test_get(self):
        ex = ExaminationsView(app, exs)
        server.start()

        add_patients()
        
        resp = requests.get(url)
        self.assertEqual(len(resp.json()), 4)

        server.shutdown()
        server.join()
    
    def test_delete(self):
        ex = ExaminationsView(app, exs)
        server.start()

        add_patients()
        
        resp1 = requests.get(url)

        requests.delete(url, json={'item':{'examination_id':1}})
        requests.delete(url, json={'item':{'examination_id':3}})
        
        resp2 = requests.get(url)

        server.shutdown()
        server.join()

        self.assertEqual(len(resp1.json()), 4)
        self.assertEqual(len(resp2.json()), 2)

        self.assertIn(str(2), resp2.json().keys())
        self.assertIn(str(4), resp2.json().keys())
        self.assertNotIn(str(1), resp2.json().keys())
        self.assertNotIn(str(3), resp2.json().keys())
    
    def test_get_config(self):
        ex = ExaminationsView(app, exs)
        server.start()
        resp = requests.get(url, json={'command': 'config'})
        self.assertIsNotNone(resp)
        self.assertIn('auto_pick', resp.json())
        server.shutdown()
        server.join()

    def test_get_sparse(self):
        ex = ExaminationsView(app, exs)
        server.start()

        add_patients()

        resp = requests.get(url, json={'command': 'item', 'data': 1})
        self.assertIsNotNone(resp)
        self.assertEqual(1, resp.json()['examination_id'])

        resp = requests.get(url, json={'command': 'item', 'data': [1, 2]})
        sparse = resp.json()
        self.assertEqual(len(sparse), 2)
        self.assertEqual(1, sparse[0]['examination_id'])
        self.assertEqual(2, sparse[1]['examination_id'])
        
        server.shutdown()
        server.join()


    def test_set_config(self):
        ex = ExaminationsView(app, exs)
        server.start()

        config = exs.get_config()
        self.assertTrue(config['auto_pick'])
        
        resp = requests.put(url, json={'command': 'config', 'data': {'auto_pick': False}})
        config = exs.get_config()
        self.assertFalse(config['auto_pick'])

        server.shutdown()
        server.join()
