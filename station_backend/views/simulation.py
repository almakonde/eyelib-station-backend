import math

from mjk_backend.restful import Restful
from flask import Flask, jsonify, make_response, request


timescaling_encoding = {
    1: 0.25,
    2: 0.5,
    3: 1.0,
    4: 2.0,
    5: 3.0
}

class SimulationView(Restful):

    def __init__(self, app, sim, *args, **kwargs):
        name = kwargs.get('name', 'simulation')
        super().__init__(app, name=name)
        self._sim = sim
        self.commands = {
            'get_timescaling': self._get_timescaling,
            'put_timescaling': self._put_timescaling,
        }

    def get(self, *args, **kwargs):
        if request.is_json:
            command = request.json.get('command', '')
        else:
            command = request.args.get('command', '')

        if request.is_json:
            data = request.json.get('data', None)
        else:
            data = request.args.get('data', None)

        if command in self.commands.keys():
            return self.commands[command](data)
        else:
            return jsonify({})

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

    def _get_ts_encoding(self, value):
        ret = 3
        for encoding, ts in timescaling_encoding.items():
            if math.isclose(ts, value):
                ret = encoding
                break
        return ret

    def _get_timescaling(self, data):
        return {"value": self._get_ts_encoding(self._sim.get_timescaling())}


    def _put_timescaling(self, data):
        value = timescaling_encoding.get(data, 1.0)
        self._sim.set_timescaling(value)
        return {"value": self._get_ts_encoding(self._sim.get_timescaling())}
