from pytest import fixture

from flask import Flask

from station_backend.views.examinations import Examinations, ExaminationsView
from mjk_backend.threaded_server import ThreadedServer

@fixture(scope='function')
def patients():
    return [
    {'patient_name': 'George', 'patient_id': 1},
    {'patient_name': 'Paul', 'patient_id': 2},
    {'patient_name': 'John', 'patient_id': 3},
    {'patient_name': 'Ringo', 'patient_id': 4}
]

@fixture(scope='function')
def requests_server():
    app = Flask("test_examination")
    server = ThreadedServer(app, 'test')
    url = 'http://127.0.0.1:5000/examinations'
    exs = Examinations()
    return server, url, exs