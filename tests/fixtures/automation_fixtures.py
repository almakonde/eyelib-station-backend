'''
Automation Fixtures

These are the fixtures necessary to run the automation tests for station_backend.
'''
# from pytest import fixture

# from flask import Flask
# from mjk_backend.threaded_server import ThreadedServer

# from station_common.automation.patient_station import PatientStationAutomation
# from station_common.connection import connection_factory
# from station_common.platform import EyeLibPlatform
# from station_backend.views.automation import AutomationView

# @fixture(scope='function')
# def patient_station_automation():
#     psa = None
#     con = connection_factory('sim0')
#     con.open()
#     platform = EyeLibPlatform([con])
#     if platform:
#         platform.populate()
#         station = platform.patient_stations.get('PS1', None)
#         if station:
#             psa = PatientStationAutomation(station)
#     return psa


# @fixture(scope='function')
# def server_automation(patient_station_automation):
#     app = Flask("test_safety")
#     server = ThreadedServer(app, 'test')
#     server.start()
#     url = 'http://127.0.0.1:5000/safety'
#     psa = patient_station_automation
#     AutomationView(app, psa)
#     yield server, url, psa
#     server.shutdown()
#     server.join()
