from flask import Flask, jsonify, request, make_response
from mjk_backend.restful import Restful
from station_common.automation.patient_station import PatientStationAutomation, logger
from station_backend.utilities.decoraters import roles_required

from station_backend import sse

class PatientAdjustView(Restful):
    def __init__(self, app: Flask, psa: PatientStationAutomation):
        super().__init__(app, 'patient_adjust')
        self._psa = psa
        self._ps = psa.patient_station

        self._ps.axes['ChinRest'].bind('position_mm', self._on_crz_changed)
        self._ps.sh_axes['StationHeight'].bind('position_mm', self._on_station_height_changed)

    @roles_required("stationFrontendAllowed")
    def get(self, *args, **kwargs):
        # Collect data for station-frontend from station-common
        data = {            
            'chin_z': self._psa.chin_z_from_station_height(),
            'chinrest_z': self._psa.chinrest_z(),
            # fixed values, defined at initialization from sim0.xml            
            'chin_z_min': self._psa.chin_z_min(),
            'chin_z_max': self._psa.chin_z_max(),
            'chin_to_eyeline_max': self._psa.chin_to_eyeline_max(),
            'chin_to_eyeline_min': self._psa.chin_to_eyeline_min(),
            'chinrest_length': self._psa.chinrest_length()
        }
        return jsonify(data)

    @roles_required("stationFrontendAllowed")
    def put(self, *args, **kwargs):
        command = request.json.get('command', None)
        if command is not None:
            data = request.json.get('data', None)
            if data is not None:
                if command == 'chin_z':
                    height = self._psa.station_height_from_chin_z(data)
                    self._ps.sh_axes['StationHeight'].move_to_mm(height)
                    return jsonify({})
                elif command == 'chinrest_z':
                    self._ps.axes['ChinRest'].move_to_mm(data)
                    return jsonify({})
                elif command == 'sit_down':
                    sitting_down_flag = self._psa.set_station_height(data)
                    return jsonify({'sitting_down':sitting_down_flag})
                else:
                    return make_response('unknown command', 500)
            else:
                return make_response('no data', 500)    
        else:
            return make_response('no command', 500)

    @roles_required("stationFrontendAllowed")
    def _on_crz_changed(self, *args, **kwargs):        
        chinrest_pos = self._psa.chinrest_z()
        # logger.info("sse.push: chinrest_z=%f",chinrest_z)
        sse.push('patient_adjust', 'chinrest_z', chinrest_pos)


    def _on_station_height_changed(self, *args, **kwargs):
        chin_z = self._psa.chin_z_from_station_height()
        # logger.info("sse.push: chin_z=%f",chin_z)
        sse.push('patient_adjust', 'chin_z', chin_z)
