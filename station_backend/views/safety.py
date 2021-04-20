from mjk_backend.restful import Restful
from flask import Flask, jsonify
from station_common.safety import Safety


class SafetyView(Restful):

    def __init__(self, app: Flask, safety: Safety):
        super().__init__(app, 'safety')
        self._safety = safety
      
    def get(self, *args, **kwargs):
        ret = {
            symbol.variable: symbol.read() for symbol in self._safety.symbols.values()
            }
        return jsonify(ret)
