from flask import jsonify, request, make_response
from mjk_backend.restful import Restful

from station_backend.views.side_camera import SideCameraView
from station_common.automation.patient_station import PatientStationAutomation
from station_backend.utilities.decoraters import roles_required

from station_backend import sse
import time

class SideCamerasView(Restful):

    def __init__(self, app, platform, patient_station, psa: PatientStationAutomation):
        super().__init__(app, 'sidecameras', path='/sidecameras')
        self.psa = psa
        self.ps = patient_station
        if platform is not None:
            self.storage = platform.instrument_storage
            self.iids = ['SC-R','SC-L']
            self.types = ['SideCamera-Right','SideCamera-Left']
            self.urls = ['http://localhost:5011', 'http://localhost:5012']

        for iid, type, url in zip(self.iids, self.types, self.urls):          
            side_camera_view = SideCameraView(app, psa, iid, type, url)

        self.commands = {
            'eyes': self._put_eyes
        }    

    @roles_required("stationFrontendAllowed")
    def get(self, *args, **kwargs):
        data = {
            'instruments': self.iids,
            'current': 'Test',
            'instruments_types': self.types
        }
        return jsonify(data)

    @roles_required("stationFrontendAllowed")
    def put(self, *args, **kwargs):
        command = request.json.get('command', None)
        if command is not None:
            data = request.json.get('data')
            if command in self.commands.keys():
                return self.commands[command](data)
            else:
                return make_response('command not found', 500)
        else:
            return make_response('no command provided', 500)


    @roles_required("stationFrontendAllowed")
    def _put_eyes(self, *args, **kwargs):        
        return jsonify({})