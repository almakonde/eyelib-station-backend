'''
Automation Fixtures

These are the fixtures necessary to run the automation tests for station_backend.
'''
import os
import requests
import threading
from pytest import fixture

from flask import Flask, request

from station_common.automation.platform import PlatformAutomation
from station_common.connection import connection_factory
from station_common.implementation.sim.gen2 import gen2_simulation
from station_common.platform import EyeLibPlatform
from station_backend import sse
from station_backend.views.automation import AutomationView
from station_backend.views.persistence import PersistenceView

def die():
    '''https://stackoverflow.com/a/26788325/2571805'''
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return "Shutting down..."


def patient_station_automation(app):
    persistence_filename = os.path.join(os.getcwd(), 'sim0.xml')
    persistence_view = PersistenceView(app, path=persistence_filename)
    persistence_view.load()
    station = pa = None
    sim = gen2_simulation('sim0')
    con = connection_factory('sim0')
    print(f'[patient_station_automation]: got con={con}')
    if con:
        con.open()
        if con.is_open:
            if not persistence_view.load():
                print(f"Failed to load persistence data from file {persistence_filename}")
            platform = EyeLibPlatform([con])
            if platform:
                platform.populate()
                station = platform.patient_stations.get('PS1', None)
                if station:
                    pa = PlatformAutomation(platform)
    return station, pa, sim


@fixture(scope='class')
def server_automation():
    print(f"{64*'='}\nAutomation Fixtures\n{64*'='}\n")
    app = Flask("test_automation", static_url_path='', static_folder='static', template_folder='web/templates')
    app.testing = True
    app.env = 'Testing'
    app.add_url_rule('/die', 'die', die)
    server = threading.Thread(target=lambda: app.run(debug=True, port=5001, use_reloader=False))
    server.start()
    url = 'http://localhost:5001/automation'
    psa = av = None
    sse.Sse(app)
    station, pa, sim = patient_station_automation(app)
    if pa is not None:
        psa = pa.psas[station]
        av = AutomationView(app, psa)
        pa.start()
    yield url, psa, av, sim
    print('[server_automation] dying...')
    # os.kill(os.getpid(), 9)
    requests.get('http://localhost:5001/die')


