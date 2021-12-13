from mjk_backend.restful import Restful
from flask import jsonify, request

import time
import station_common


#axis_keys = ['name', 'state', 'mode', 'length_mm', 'position_mm', 'speed_mm_s', 'limit_A', 'limit_B']

class PowerView(Restful):
    def __init__(self, app, *args, **kwargs):
        self.pwr = kwargs.pop("pwr", None)
        super().__init__(app, 'pwr', *args, **kwargs)
        self._app.add_url_rule(self._path+'/<pwr_id>', self._name+'_ids', self.restful, methods=['GET', 'PUT'])

    def get(self, *args, **kwargs):
        data = []
        pwr_id = kwargs.get('pwr_id', None)
        print(f'\nGot in GET...\n\t{args}\n\t{kwargs}')
        if pwr_id:
            pwr_sw = self.pwr.pwr_sws.get(pwr_id, None)
            if pwr_sw:
                data = {pwr_id: pwr_sw.state}
        else:
            print(self.pwr)
            data = list(self.pwr.pwr_sws.keys())
        return jsonify(data)

    def put(self, *args, **kwargs):
        data = {}
        pwr_id = kwargs.get('pwr_id', None)
        if pwr_id:
            pwr_sw = self.pwr.pwr_sws.get(pwr_id, None)
            if pwr_sw:
                value = request.json.get('value', None)
                pwr_sw.set_state(value)
        return jsonify(data)
