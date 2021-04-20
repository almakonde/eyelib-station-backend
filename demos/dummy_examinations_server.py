from station_backend.views.examinations import Examinations, ExaminationsView
from mjk_backend.threaded_server import ThreadedServer
from mjk_utils.scheduling import PeriodicTask
from flask import Flask
from flask_cors import CORS
import requests
import queue
app = Flask("test_examination")
app.testing = True
app.secret_key = 'testing'

# app.config.update(
#             SECRET_KEY='testing',
#             SESSION_COOKIE_DOMAIN='.example.com',
#             SESSION_COOKIE_HTTPONLY=False,
#             SESSION_COOKIE_SECURE=True,
#             SESSION_COOKIE_PATH='/'
#         )


server = ThreadedServer(app, 'test', port=5003)

CORS(app)

url = 'http://127.0.0.1:5003/examinations'


class DummyPatientStation:
    def __init__(self, exs: Examinations):
        self._task = PeriodicTask(self._iterate_, 1)
        self._state = 'idle'
        self._exs = exs
        self._current_ex = None
        self._counter = 0
        self._queue = queue.Queue

    def start(self):
        self._task.start()
    
    def stop(self):
        self._task.stop()

    def _iterate_(self, *args, **kwargs):
        self._counter += 1

        if self._state == 'idle':
            self._current_ex = self._exs.get_next_examination(block=True)
            if self._current_ex is not None:
                self._state = 'preparing'

        elif self._state == 'preparing':
            if self._counter >= 3:
                self._state = 'waiting_patient'
                self._counter = 0

        elif self._state == 'waiting_patient':
            if self._counter >= 5:
                self._exs.set_status(self._current_ex['examination_id'], 'waiting_patient')
                self._state = 'processing'
                self._counter = 0

        elif self._state == 'processing':
            if self._counter >= 15:
                self._exs.set_status(self._current_ex['examination_id'], 'ongoing')
                self._state = 'done'
                self._counter = 0
        
        elif self._state == 'done':
            self._exs.set_status(self._current_ex['examination_id'], 'done')
            self._state = 'idle'




exs = Examinations()


def picker(*args, **kwargs):
    exs._pick_next()


#pick_task = PeriodicTask(picker, 3)


station = DummyPatientStation(exs)

patients = [
    {'patient_name': 'Henry', 'patient_id':1},
    {'patient_name': 'Paul', 'patient_id':2},
    {'patient_name': 'John', 'patient_id':3},
    {'patient_name': 'Ringo', 'patient_id':4}
]

ex = ExaminationsView(app, exs)

station.start()
#pick_task.start()
exs.start()
server.start()

for patient in patients:
    resp = requests.put(url, json={'command':'examinations', 'data': exs.factory(**patient)})


server.join()

station.stop()
exs.stop()