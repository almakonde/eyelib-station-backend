'''
Safety Fixtures

These are the fixtures necessary to run the safety tests for station_backend.
'''
from pytest import fixture

from flask import Flask
from mjk_backend.threaded_server import ThreadedServer

from station_common.implementation.sim.simulation import Symbol
from station_backend.views.safety import Safety, SafetyView

@fixture(scope='function')
def symbol_safety():
    return lambda module_name, symbol_name: Symbol(module_name, symbol_name, type_name='BOOL')

@fixture(scope='function')
def server_safety():
    app = Flask("test_safety")
    server = ThreadedServer(app, 'test')
    server.start()
    url = 'http://127.0.0.1:5000/safety'
    safety = Safety()
    SafetyView(app, safety)
    yield url, safety
    server.shutdown()
    server.join()
