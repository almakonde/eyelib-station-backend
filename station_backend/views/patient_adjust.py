from flask import Flask, jsonify, request, make_response
from mjk_backend.restful import Restful
from station_common.automation.patient_station import PatientStationAutomation
from station_backend.utilities.decoraters import roles_required

from station_backend import sse

class PatientAdjustView(Restful):
    def __init__(self, app: Flask, psa: PatientStationAutomation):
        super().__init__(app, 'patient_adjust')
        self._psa = psa
        self._ps = psa.patient_station

        self._ps.axes['HeadRest_Z'].bind('position_mm', self._on_hrz_changed)
        self._ps.axes['FrontPanel'].bind('position_mm', self._on_fp_changed)

    @roles_required("stationFrontendAllowed")
    def get(self, *args, **kwargs):
        data = {
            'chin_z': self._psa.chin_z_from_front_panel(),
            'chin_to_eyeline': self._psa.chin_to_eyeline_from_headrest_z(),
            'chin_to_eyeline_min': self._psa.chin_to_eyeline_min(),
            'chin_z_max': self._psa.chin_z_max(),
            'chin_to_eyeline_max': self._psa.chin_to_eyeline_max(),
            'chin_z_min': self._psa.chin_z_min()
        }
        return jsonify(data)

    @roles_required("stationFrontendAllowed")
    def put(self, *args, **kwargs):
        command = request.json.get('command', None)
        if command is not None:
            data = request.json.get('data', None)
            if data is not None:
                if command == 'chin_z':
                    fp = self._psa.front_panel_from_chin_z(data)
                    self._ps.axes['FrontPanel'].move_to_mm(fp)
                    return jsonify({})
                elif command == 'chin_to_eyeline':
                    fp = self._psa.headrest_from_chin_to_eyeline(data)
                    self._ps.axes['HeadRest_Z'].move_to_mm(fp)
                    return jsonify({})
                else:
                    return make_response('unknown command', 500)
            else:
                return make_response('no data', 500)    
        else:
            return make_response('no command', 500)

    @roles_required("stationFrontendAllowed")
    def _on_hrz_changed(self, *args, **kwargs):
        chin_to_eyeline = self._psa.chin_to_eyeline_from_headrest_z()
        sse.push('patient_adjust', 'chin_to_eyeline', chin_to_eyeline)


    def _on_fp_changed(self, *args, **kwargs):
        chin_z = self._psa.chin_z_from_front_panel()
        sse.push('patient_adjust', 'chin_z', chin_z)
