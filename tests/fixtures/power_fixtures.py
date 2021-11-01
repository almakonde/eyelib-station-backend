'''
Power Fixtures

These are the fixtures necessary to run the power tests for station_backend.
'''
from pytest import fixture
from tests.fixtures.automation_fixtures import patient_station_automation
from flask import Flask
from mjk_backend.threaded_server import ThreadedServer

from station_backend.views.pwr import PowerView
from station_backend.views.symbols import SymbolManager

@fixture(scope='function')
def server_power():
    app = Flask("test_power")
    server = ThreadedServer(app, 'test')
    server.start()
    url = 'http://127.0.0.1:5000/pwr'
    station, _, _ = patient_station_automation(app)
    symbol_manager = SymbolManager(app)
    for pwr_switch in station.pwr.pwr_sws.values():
        path = "/pwr/"+pwr_switch.symbol.variable
        symbol_manager.register_symbol(pwr_switch.symbol, path=path)
    pv = PowerView(app, pwr=station.pwr)
    print(f'URL map: {app.url_map}')
    yield url, station, pv
    server.shutdown()
    server.join()
