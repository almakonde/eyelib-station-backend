from mjk_backend.restful import Restful
from flask import jsonify
from station_backend.utilities.decoraters import roles_required

class AxesView(Restful):

    def __init__(self, app, patient_station):
        super().__init__(app, 'axes')
        self.patient_station = patient_station

    @roles_required("stationFrontendAllowed")
    def get(self, *args, **kwargs):
        if self.patient_station:
            data = {'axes': list(self.patient_station.axes.keys())}
        else:
            data = {'error': "no station"}
        return jsonify(data)


class SHAxesView(Restful):

    def __init__(self, app, patient_station):
        super().__init__(app, 'sh_axes')
        self.patient_station = patient_station

    @roles_required("stationFrontendAllowed")
    def get(self, *args, **kwargs):
        if self.patient_station:
            data = {'sh_axes': list(self.patient_station.sh_axes.keys())}
        else:
            data = {'error': "no station"}
        return jsonify(data)
