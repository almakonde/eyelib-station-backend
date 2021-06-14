from mjk_backend.restful import Restful
from station_common.examinations import Examinations
from flask import request, jsonify, session, sessions
import queue
from station_backend.utilities.decoraters import roles_required


class ExaminationsView(Restful):
    def __init__(self, app, exs: Examinations):
        super().__init__(app, 'examinations')
        self._exs = exs
        self._exs.start()

    def stop(self):
        self._exs.stop()

    @roles_required("stationFrontendAllowed")
    def get(self, *args, **kwargs):
        
        if request.is_json:
            command = request.json.get('command', 'all')
        else:
            command = request.args.get('command', 'all')

        if command == 'all':
            return jsonify(self._exs.get())
        elif command == 'config':
            return jsonify(self._exs.get_config())
        elif command == 'item':
            exid = request.json.get('data', None)
            if exid is not None:
                return jsonify(self._exs.get(exid))
            else:
                return jsonify({})
        else:
            return jsonify({})

    @roles_required("stationFrontendAllowed")
    def put(self, *args, **kwargs):
        ret = False
        command = request.json.get('command', None)
        if command is not None:
            data = request.json.get('data')
            if command == 'examinations':
                ret = self._exs.push(data)
            elif command == 'config':
                self._exs.set_config(data)
                ret = True
            elif command == 'cancel':
                if 'examination_id' in data.keys():
                    self._exs.cancel(data['examination_id'])
                    ret = True
            elif command == 'respool':
                if 'examination_id' in data.keys():
                    ret = self._exs.respool(data['examination_id'])
            elif command == 'pick':
                if 'examination_id' in data.keys():
                    self._exs.manual_pick(data['examination_id'])

        # add = request.json.get('add', None)
        # if add is not None:
        #     push_ret = self._exs.push(add)
        #     ret = (push_ret is not None)
        
        return jsonify({'ret':ret})

    @roles_required("stationFrontendAllowed")
    def delete(self, *args, **kwargs):
        ret = False
        item = request.json.get('item', None)
        if item is not None:
            ret = self._exs.delete(item.get('examination_id', None))
        return jsonify({'ret':ret})
