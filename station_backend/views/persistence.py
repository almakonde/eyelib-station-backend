from mjk_backend.restful import Restful
from mjk_utils.persistence import Persistence
from flask import Flask, request, make_response, jsonify

class PersistenceView(Restful):

    def __init__(self, app, *args, **kwargs):
        super().__init__(app, 'persistence')
        self._filepath = kwargs.get("path", None)

    def load(self):
        ret = False
        if self._filepath is not None:
            try:
                Persistence().from_file(self._filepath)
                ret = True
            except:
                ret = False
        return ret

    def save(self):
        ret = False
        if self._filepath is not None:
            try:
                Persistence().to_file(self._filepath)
                ret = True
            except:
                ret = False
        return ret

    def get(self, *args, **kwargs):
        pass
        # if request.is_json:
        #     command = request.json.get('command', None)
        #     data = request.json.get('data', None)
        # else:
        #     command = request.args.get('command', None)
        #     dstr = request.args.get('data', None)            
        #     data = json.loads(dstr) if dstr is not None else None


    def put(self, *args, **kwargs):
        command = request.json.get('command', None)
        ret = None
        if command is not None:
            # data = request.json.get('data')
            if command == 'load':
                ret = self.load()
            elif command == 'save':
                ret = self.save()
        if ret is not None:
            return jsonify(ret)
        else:
            return make_response("command failed", 500)
