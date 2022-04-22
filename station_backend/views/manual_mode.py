from flask import jsonify, request, make_response

from mjk_backend.restful import Restful
from station_common.automation.patient_station import PatientStationAutomation

from station_backend.utilities.decoraters import roles_required


class ManualModeView(Restful):

    def __init__(self, app, platform, patient_station, psa: PatientStationAutomation):
        super().__init__(app, 'manual_mode', path='/manual_mode')
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
        self.commands = {
            'manual_exam': self._put_manual_exam,
            'manual_exam_done': self._put_manual_exam_done,
            'auto_chinrest_adjust': self._auto_chinrest_adjust
        }
        self.examination_started = False


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
    def _put_manual_exam(self, *args, **kwargs):
        data = args[0]
        iid = data.get('instrument', None)
        if iid is None:
            slot = data.get('slot', None)
        else:
            if iid in self.instruments:
                instrument = self.storage.get_instrument_from_iid(iid)
                if instrument is not None:
                    self.psa.manual_exam_mode(instrument)
                    ret = jsonify({})
        if ret is None:
            return make_response('manual_exam failed', 500)
        else:
            return ret        
    
    @roles_required("stationFrontendAllowed")
    def _put_manual_exam_done(self, *args, **kwargs):
        self.psa.namespace.manual_exam_done = True
        return True

    @roles_required("stationFrontendAllowed")
    def _auto_chinrest_adjust(self, *args, **kwargs):
        self.psa.chinrest_adjustment_mode()
        return True
