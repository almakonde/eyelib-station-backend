from flask import Flask, jsonify, request, make_response
from station_common.automation.platform import PlatformAutomation
from station_common.automation.patient_station import PatientStationAutomation
from mjk_backend.restful import Restful
from mjk_backend.stream import Stream

from station_common.automation.platform import logger

from station_backend import sse


class StationView(Restful, Stream):

    def __init__(self, app: Flask, psa: PatientStationAutomation):
        super().__init__(app, 'station')
        # self._path = '/station'
        # self._stream_path = "%s/sse" % self._path
        # Restful.__init__(self, app, name=self._path.replace('/',''), path=self._path)
        # Stream.__init__(self, app, path=self._stream_path, stream_queue_size=100, put_block=False)
        self.psa = psa
        self.psa.patient_station.bind('examination', self._on_examination_changed)
        self.putcommands = {
            'audio_speech': self.audio_speech,
            'pick_examination': self.pick_examination,
        }
        self.getcommands = {
            'view': self.view,
            'bc': self.bc,
            'bc_trigger': self.bc_trigger,
            'audio_speech': self.audio_speech,
        }

        self.psa.patient_station.back_camera.bind('last_measurement', self.on_bc_last_measurement_changed)
        self.psa.patient_station.back_camera.bind('last_extents_mm', self.on_bc_last_extents_mm_changed)


    def get(self, *args, **kwargs):
        if request.is_json:
            command = request.json.get('command', 'show')
        else:
            command = request.args.get('command', 'show')

        if request.is_json:
            data = request.json.get('data', None)
        else:
            data = request.args.get('data', None)

        if command in self.getcommands.keys():
            return self.getcommands[command](data)
        else:
            return make_response('command not found', 500)

    def put(self, *args, **kwargs):
        command = request.json.get('command', None)
        if command is not None:
            data = request.json.get('data')
            if command in self.putcommands.keys():
                return self.putcommands[command](data)
            else:
                return make_response('command not found', 500)
        else:
            return make_response('no command provided', 500)

    # def push_event(self, event, data):
    #     self.push_item({'event': event, 'data': data})

    def view(self, data):
        ret = {}
        if self.psa.patient_station.examination is not None:
            ret = {k:v for k,v in self.psa.patient_station.examination.items() if k!='slots'}
        return ret

    def bc(self, data):
        return {
                'tc_url': self.psa.patient_station.back_camera.tc_settings['url'],
                'eyeline_target':self.psa.patient_station.back_camera.eyeline_target,
                'extents_mm': self.psa.patient_station.back_camera.get_extents_mm()
                }

    def bc_trigger(self, data):
        try:
            self.psa.patient_station.back_camera.measure()
        except:
            pass
        return {}

    def pick_examination(self, data):
        self.psa.patient_station.next_patient_examination()
        if self.psa.patient_station.examination is not None:
            id = self.psa.patient_station.examination.get('examination_id', None)
            if id is not None:
                return jsonify({'examination_id': id})
            else:
                return jsonify({})
        else:
            return jsonify({})

    def audio_speech(self, data):
        sentence = data
        if self.psa.patient_station.patient_interaction is not None:
            self.psa.patient_station.patient_interaction.say(sentence)

    def _on_examination_changed(self, *args, **kwargs):
        sse.push('station', 'examination', self.psa.patient_station.examination)

    def on_bc_last_measurement_changed(self, back_camera, data):
        key, value, old_value = data
        # logger.info("sse.push bc_measurement: %s",value)
        sse.push('station', 'bc_measurement', value)

    def on_bc_last_extents_mm_changed(self, back_camera, data):
        key, value, old_value = data
        sse.push('station', 'bc_extents_mm', value)