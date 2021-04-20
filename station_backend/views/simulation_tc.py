from mjk_utils.cmd import script_dir
from mjk_backend.restful import Restful
from mjk_backend.stream import Stream
from flask import Flask, jsonify
from station_common.patient_station import PatientStation
from station_common.instrument import Instrument
import json


RESDIR = script_dir()+'/res/tc'


class SimulationTrackingCamera(Restful, Stream):

    def __init__(self, app: Flask, patient_station: PatientStation, instrument: Instrument, **kwargs):
        self._path = kwargs.get('path', '/tc')
        self._stream_path = "%s/sse" % self._path
        Restful.__init__(self, app, name=self._path.replace('/',''), path=self._path)
        Stream.__init__(self, app, path=self._stream_path, stream_queue_size=100, put_block=False)
        self._ps = patient_station
        self._instrument = instrument
        self._pixel_to_mm_ratio = 0.5

        self._tray_z_rel_mm = kwargs.get("tray_z_rel_mm", 0.0)
           
        self._ps.axes['InstrumentTable_X'].bind('position_mm', self.on_x_movement)
        self._ps.axes['InstrumentTable_Y'].bind('position_mm', self.on_y_movement)
        self._ps.axes['InstrumentTable_Z'].bind('position_mm', self.on_z_movement)
        self._ps.axes['HeadRest_Z'].bind('position_mm', self.on_hr_movement)
        self._ps.bind('instrument', self.on_instrument_changed)
        self._ps.safety.bind('presence', self.on_presence_changed)


    def _get_tbz_rel(self):
        tbz_rel = 0.0
        table_fp_ref = self._ps.tbl_fp
        point = table_fp_ref.taught_points['Table/Front Panel Reference']
        if self._ps.axes['FrontPanel'].position_mm is not None and self._ps.axes['InstrumentTable_Z'].position_mm is not None:
            fp_rel_offset =  self._ps.axes['FrontPanel'].position_mm - point['front panel']
            tbz_rel_offset = self._ps.axes['InstrumentTable_Z'].position_mm - point['table z'] 
            tbz_rel = tbz_rel_offset - fp_rel_offset
        return tbz_rel

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
            'relative_z_mm': 0.0,
            'tc_z_offset': self._instrument.parameters['p2tc']['z'],
            'tray_z_rel_mm': self._tray_z_rel_mm,
            'presence': self._ps.safety.presence
        }
        if self._ps.instrument is not None:
            if self._ps.instrument == self._instrument:
                data['activated'] = True
                if hasattr(self._ps.instrument, 'camera_plane'):
                    data['pixel_to_mm_ratio'] = self._ps.instrument.camera_plane.alpha * self._ps.instrument.camera_plane.gamma # (beta is ignored as sim is perfect)
                    data['tc_z_offset'] = self._ps.instrument.parameters['p2tc']['z']

        data['relative_z_mm'] = self._get_tbz_rel()
        data['relative_y_mm'] = self._get_tby_rel()
        if self._ps.axes['HeadRest_Z'].position_mm is not None:
            data['hr_mm'] = self._ps.axes['HeadRest_Z'].position_mm
        else:
            data['hr_mm'] = 0.0

        return jsonify(data)


    def push_event(self, event, data):
        self.push_item({'event': event, 'data': data})

    def on_x_movement(self, *args, **kwargs):
        if self._ps.instrument is not None:
            if self._ps.instrument == self._instrument:
                if hasattr(self._ps.instrument, 'camera_plane'):
                    depth = self._instrument.tracking_camera_depth(self._ps.get_plate_depth())
                    self._instrument.camera_plane.set_current_depth(depth)
                    self._pixel_to_mm_ratio = self._ps.instrument.camera_plane.alpha * self._ps.instrument.camera_plane.gamma # (beta is ignored as sim is perfect)
                    
            else:
                self._pixel_to_mm_ratio = 0.5

        self.push_event('tbx', {'pixel_to_mm_ratio': self._pixel_to_mm_ratio}) #push image moved/cropped/zoomed in regards to position

    def on_y_movement(self, *args, **kwargs):
        self.push_event('tby', {'relative_y_mm': self._get_tby_rel()})

    def on_z_movement(self, *args, **kwargs):
        self.push_event('tbz', {'relative_z_mm': self._get_tbz_rel()})

    def on_hr_movement(self, *args, **kwargs):
        self.push_event('hr', {'hr_mm': self._ps.axes['HeadRest_Z'].position_mm})

    def on_instrument_changed(self, *args, **kwargs):
        activated = False
        if self._ps.instrument is not None:
            if self._ps.instrument == self._instrument:
                activated = True
        
        self.push_event('instrument', {'activated': activated})

    def on_presence_changed(self, *args, **kwargs):
        self.push_event('presence', {'presence': self._ps.safety.presence})

    def push_event(self, event, data):
        self.push_item({'event': event, 'data': data})

    def generate_item(self, item):
        return 'event:'+item['event']+'\ndata:'+json.dumps(item)+'\n\n'
        #return json.dumps(item)
        #b'\r\n--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + item + b'\r\n'