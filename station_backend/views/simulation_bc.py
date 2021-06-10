from mjk_utils.cmd import script_dir
from mjk_backend.restful import Restful
from mjk_backend.stream import Stream
from flask import Flask, jsonify
from station_common.patient_station import PatientStation
from station_common.back_camera import BackCamera
import json


RESDIR = script_dir()+'/res/tc'


class SimulationBackCamera(Restful, Stream):

    def __init__(self, app: Flask, patient_station: PatientStation, **kwargs):
        self._path = kwargs.get('path', '/bc')
        self._stream_path = "%s/sse" % self._path
        Restful.__init__(self, app, name=self._path.replace('/',''), path=self._path)
        Stream.__init__(self, app, path=self._stream_path, stream_queue_size=100, put_block=False)
        self._ps = patient_station
        self._pixel_to_mm_ratio = self._ps.back_camera.camera.camera_plane.pixels_to_mm_x(1.0)
        self._tray_z_rel_mm = kwargs.get("tray_z_rel_mm", 0.0)

        '''
        When one of the following _ps properties is changed the a function is called (self.on_...).
        The function push an event. 
        The event is treated on the station-rtcu/sim.py _events_run loop.
        ''' 
        # self._ps.axes['InstrumentTable_X'].bind('position_mm', self.on_x_movement)
        self._ps.axes['InstrumentTable_Y'].bind('position_mm', self.on_y_movement)
        self._ps.axes['ChinRest_Z'].bind('position_mm', self.on_cr_movement)
        self._ps.safety.bind('presence', self.on_presence_changed)


    def _get_tby_rel(self):
        ret = 0.0
        if self._ps.axes['InstrumentTable_Y'].length_mm is not None and self._ps.axes['InstrumentTable_Y'].position_mm is not None:
            tby_length = self._ps.axes['InstrumentTable_Y'].length_mm
            tby_pos = self._ps.axes['InstrumentTable_Y'].position_mm
            ret = tby_pos - tby_length/2
        return ret


    def get(self):
        data = {
            'activated': False,
            'pixel_to_mm_ratio': self._pixel_to_mm_ratio,
            'presence': self._ps.safety.presence
        }
     
        data['relative_y_mm'] = self._get_tby_rel()
        if self._ps.axes['ChinRest_Z'].position_mm is not None:
            data['cr_mm'] = self._ps.axes['ChinRest_Z'].position_mm
        else:
            data['cr_mm'] = 0.0

        return jsonify(data)


    def push_event(self, event, data):
        self.push_item({'event': event, 'data': data})

    # def on_x_movement(self, *args, **kwargs):
    #     if self._ps.instrument is not None:
    #         if self._ps.instrument == self._instrument:
    #             if hasattr(self._ps.instrument, 'camera_plane'):
    #                 depth = self._instrument.tracking_camera_depth(self._ps.get_plate_depth())
    #                 self._instrument.camera_plane.set_current_depth(depth)
    #                 self._pixel_to_mm_ratio = self._ps.instrument.camera_plane.alpha * self._ps.instrument.camera_plane.gamma # (beta is ignored as sim is perfect)
                    
    #         else:
    #             self._pixel_to_mm_ratio = 0.5

    #     self.push_event('tbx', {'pixel_to_mm_ratio': self._pixel_to_mm_ratio}) #push image moved/cropped/zoomed in regards to position

    def on_y_movement(self, *args, **kwargs):
        self.push_event('tby', {'relative_y_mm': self._get_tby_rel()})

    def on_cr_movement(self, *args, **kwargs):
        self.push_event('cr', {'cr_mm': self._ps.axes['ChinRest_Z'].position_mm})

    def on_presence_changed(self, *args, **kwargs):
        self.push_event('presence', {'presence': self._ps.safety.presence})

    def generate_item(self, item):
        return 'event:'+item['event']+'\ndata:'+json.dumps(item)+'\n\n'
