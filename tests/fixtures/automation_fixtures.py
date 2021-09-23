'''
Automation Fixtures

These are the fixtures necessary to run the automation tests for station_backend.
'''
import os
from pytest import fixture

from flask import Flask
from mjk_backend.threaded_server import ThreadedServer

from mjk_utils.cmd import script_dir

from station_common.automation.patient_station import PatientStationAutomation
from station_common.connection import connection_factory
from station_common.implementation.sim.connection import SimConnection
# from station_common.implementation.sim.simulation import Simulation

from station_common.implementation.sim.gen2 import gen2_simulation

from station_common.platform import EyeLibPlatform
from station_backend.views.automation import AutomationView
from station_backend.views.persistence import PersistenceView

print(f"{64*'='}\nAutomation Fixtures\n{64*'='}\n")
app = Flask("test_automation")
server = ThreadedServer(app, 'test')
server.start()

@fixture(scope='function')
def patient_station_automation():
    persistence_filename = os.path.join(os.getcwd(), 'sim0.xml')
    print(f'[patient_station_automation] persistence_filename: {persistence_filename}')
    persistence_view = PersistenceView(app, path=persistence_filename)
    persistence_view.load()
    psa = None
    sim0 = gen2_simulation('sim0')
    con = connection_factory('sim0')
    # con = SimConnection(sim0)
    print(f'[patient_station_automation]: got con={con}')
    con.open()
    platform = EyeLibPlatform([con])
    if platform:
        platform.populate()
        station = platform.patient_stations.get('PS1', None)
        if station:
            psa = PatientStationAutomation(station)
    return psa


@fixture(scope='function')
def server_automation(patient_station_automation):
    url = 'http://127.0.0.1:5000/safety'
    psa = patient_station_automation
    AutomationView(app, psa)
    yield url, psa
    server.shutdown()
    server.join()
