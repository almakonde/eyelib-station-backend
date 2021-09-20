'''
Power Fixtures

These are the fixtures necessary to run the power tests for station_backend.
'''
from pytest import fixture

from flask import Flask
from mjk_backend.threaded_server import ThreadedServer

from station_backend.views.pwr import PowerView

@fixture(scope='function')
def server_power():
    app = Flask("test_power")
    server = ThreadedServer(app, 'test')
    server.start()
    url = 'http://127.0.0.1:5000/pwr'
    PowerView(app)
    yield url
    server.shutdown()
    server.join()
