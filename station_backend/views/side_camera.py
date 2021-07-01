from flask import jsonify, request, make_response
from mjk_backend.restful import Restful


class SideCameraView(Restful):

    def __init__(self, app, psa, iid, type, url):        
        self.iid = iid.lower()
        super().__init__(app, self.iid)
        self.type = type
        self.url = url
        self.tc_url = self.url+ '/' + self.iid

    def get(self, *args, **kwargs):
        data = {
            'iid': self.iid,
            'instrument_name': self.type,
            'vendor_name': 'Mikajaki',
            'tc_url': self.tc_url            
        } 

        return jsonify(data)

    def put(self, *args, **kwargs):

        if request.is_json:
            command = request.json.get('command', None)
        else:
            command = request.args.get('command', None)

        if request.is_json:
            data = request.json.get('data', None)
        else:
            data = request.args.get('data', None)


        if command is not None:
            if command == 'eyes':                
                return jsonify({})            
            else:
                return make_response('command not found', 500)
        else:
            return make_response('no command provided', 500)