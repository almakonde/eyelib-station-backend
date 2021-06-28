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
            'chin_to_eyeline': self._psa.chin_to_eyeline_from_chinrest_z(),
            # fixed values, defined at initialization from sim0.xml
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
                    height = self._psa.station_height_from_chin_z(data)
                    self._ps.sh_axes['StationHeight'].move_to_mm(height)
                    return jsonify({})
                elif command == 'chin_to_eyeline':
                    z = self._psa.chinrest_from_chin_to_eyeline(data)
                    self._ps.axes['ChinRest'].move_to_mm(z)
                    return jsonify({})
                else:
                    return make_response('unknown command', 500)
            else:
                return make_response('no data', 500)    
        else:
            return make_response('no command', 500)

    @roles_required("stationFrontendAllowed")
    def _on_crz_changed(self, *args, **kwargs):        
        chin_to_eyeline = self._psa.chin_to_eyeline_from_chinrest_z()
        # logger.info("sse.push: chin_to_eyeline=%f",chin_to_eyeline)
        sse.push('patient_adjust', 'chin_to_eyeline', chin_to_eyeline)


    def _on_station_height_changed(self, *args, **kwargs):
        chin_z = self._psa.chin_z_from_station_height()
        # logger.info("sse.push: chin_z=%f",chin_z)
        sse.push('patient_adjust', 'chin_z', chin_z)
