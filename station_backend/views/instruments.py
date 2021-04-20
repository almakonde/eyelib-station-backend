from flask import jsonify, request, make_response
from mjk_backend.restful import Restful

from station_backend.views.instrument import InstrumentView
from station_common.automation.patient_station import PatientStationAutomation
from station_backend.utilities.decoraters import roles_required

from station_backend import sse
import time

class InstrumentsView(Restful):

    def __init__(self, app, platform, patient_station, psa: PatientStationAutomation):
        super().__init__(app, 'instruments', path='/instruments')
        self.psa = psa
        self.ps = patient_station
        if platform is not None:
            self.storage = platform.instrument_storage
            self.instruments = [iid for iid in self.storage.instruments.keys() if iid in self.storage.slot_payload.values()]

        self.instrument_types = []
        for iid in self.instruments:
            slot = self.storage.get_slot_by_iid(iid)
            if slot is not None:
                instrument = self.storage.get_instrument(slot.name)
                if instrument is not None:
                    self.instrument_types.append(instrument.instrument_name)
                    instrument_view = InstrumentView(app, psa, instrument)

        if self.ps is not None:
            self.ps.bind('instrument', self.on_current_instrument_changed)
            self.on_current_instrument_changed()

        self.commands = {
            'fetch': self._put_fetch,
            'deposit': self._put_deposit,
            'exam_only': self._put_exam_only,
            'single_full_exam': self._put_single_full_exam
        }

    def on_current_instrument_changed(self, *args, **kwargs):
        if self.ps.instrument is not None:
            self.current = self.ps.instrument.iid
        else:
            self.current = ''
        
        timestamp = time.time()
        event = '/instruments/current'
        data = {
                'type': 'instruments',
                'path': 'instruments/current',
                'name': 'current',
                'timestamp': timestamp,
                'value': self.current
                    }
        sse.push_event(event, data)

    @roles_required("stationFrontendAllowed")
    def get(self, *args, **kwargs):
        data = {
            'instruments': self.instruments,
            'current': self.current,
            'instruments_types': self.instrument_types
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
    def _put_fetch(self, *args, **kwargs):
        ret = None
        data = args[0]
        iid = data.get('instrument', None)
        if iid is None:
            slot = data.get('slot', None)
        else:
            if iid in self.instruments:
                instrument = self.storage.get_instrument_from_iid(iid)
                if instrument is not None:
                    self.psa.fetch(instrument)
                    ret = jsonify({})
        if ret is None:
            return make_response('fetch_failed', 500)
        else:
            return ret

    @roles_required("stationFrontendAllowed")
    def _put_deposit(self, *args, **kwargs):
        self.psa.deposit()
        return jsonify({})

    @roles_required("stationFrontendAllowed")
    def _put_exam_only(self, *args, **kwargs):
        self.psa.exam_only()
        return jsonify({})

    @roles_required("stationFrontendAllowed")
    def _put_single_full_exam(self, *args, **kwargs):
        data = args[0]
        iid = data.get('instrument', None)
        if iid is None:
            slot = data.get('slot', None)
        else:
            if iid in self.instruments:
                instrument = self.storage.get_instrument_from_iid(iid)
                if instrument is not None:
                    self.psa.single_full_exam(instrument)
                    ret = jsonify({})
        if ret is None:
            return make_response('single_full_exam failed', 500)
        else:
            return ret
