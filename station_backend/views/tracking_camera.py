from mjk_backend.restful import Restful
from flask import Flask, request, jsonify, make_response
from station_common.instrument import Instrument
from station_common.automation.patient_station import PatientStationAutomation
from station_common.instruments.vision.camera import TrackingCameraC2TCCalibration
from station_common.automation.waypoints import WayPoint

class TCAdjustView(Restful):
    def __init__(self, app: Flask, psa: PatientStationAutomation, instrument: Instrument, *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.psa = psa
        self.instrument = instrument
        
        self.c2tc_cal = TrackingCameraC2TCCalibration(psa.patient_station, self.instrument)

        if self.instrument is not None:
            if hasattr(self.instrument, 'tracking_camera'):
                tc = self.instrument.tracking_camera
            if hasattr(self.instrument, 'camera_plane'):
                self._cp = self.instrument.camera_plane
                if not self._cp.initialized:
                    self._cp.initialize_from_settings()

        self.adjustment_point = WayPoint('adjustment', self.psa.patient_station.table.axes,
                                            targets={'x': 0.0, 'y': 0.0, 'z': 0.0},
                                            relationships={'x': 'offset', 'y': 'offset', 'z': 'offset'})

    def get(self, *args, **kwargs):
        return jsonify({'tca':self.instrument.iid})

    def put(self, *args, **kwargs):
        command = request.json.get('command', None)
        data = request.json.get('data', None)
        if command is not None:
            if command == 'move':
                if data is not None:
                    xp = data.get('xp', None)
                    yp = data.get('yp', None)
                    if xp is not None and yp is not None:
                        self.adjust_position(xp, yp)
                else:
                    return make_response('not data', 500)
            elif command == 'set_cal_c':
                self.c2tc_cal.set_c_position()
                return jsonify({})
            elif command == 'set_cal_tc':
                self.c2tc_cal.set_tc_position()
                return jsonify({})
            elif command == 'set_cal_valid':
                self.c2tc_cal.validate()
                return jsonify({})
            elif  command == 'get_cal_corrections':
                corrections = self.c2tc_cal.get_correction()
                return jsonify(corrections)
            else:
                return make_response('unknown command', 500)
        else:
            event = request.json.get('event', None)
            if event is not None: # For legacy compat
                xp = event.get('xp', None)
                yp = event.get('yp', None)
                if xp is not None and yp is not None:
                    self.adjust_position(xp, yp)
                return jsonify({})
            else:
                return make_response('no command', 500)

    def adjust_position(self, xp: float, yp: float):

        self.psa.pause()
        if hasattr(self.instrument, 'tracking_camera_depth'):
            plate_depth = self.psa.patient_station.get_plate_depth()
            tc_depth = self.instrument.tracking_camera_depth(plate_depth)
            self._cp.set_current_depth(tc_depth)

            position = [
                xp*self._cp.image_shape[1],
                yp*self._cp.image_shape[0]
            ]

            vYZ_mm = self._cp.center_on(position)

            self.adjustment_point.targets['y'] = vYZ_mm['y']
            self.adjustment_point.targets['z'] = vYZ_mm['z']
            self.adjustment_point.goto()
        self.psa.resume()
        return jsonify(position)