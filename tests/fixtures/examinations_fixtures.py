'''
Examinations Fixtures

These are the fixtures necessary to run the examinations tests for station_backend.
'''
from pytest import fixture

from flask import Flask
from mjk_backend.threaded_server import ThreadedServer

from station_backend.views.examinations import Examinations, ExaminationsView

@fixture(scope='class')
def patients():
    return [
        {'patient_name': 'George', 'patient_id': 1},
        {'patient_name': 'Paul', 'patient_id': 2},
        {'patient_name': 'John', 'patient_id': 3},
        {'patient_name': 'Ringo', 'patient_id': 4}
    ]

@fixture(scope='function')
def server_examinations():
    app = Flask("test_examinations")
    server = ThreadedServer(app, 'test')
    server.start()
    url = 'http://127.0.0.1:5000/examinations'
    exs = Examinations()
    ExaminationsView(app, exs)
    yield server, url, exs
    server.shutdown()
    server.join()
