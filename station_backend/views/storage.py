from flask import jsonify, request
from mjk_backend.restful import Restful


class StorageView(Restful):

    def __init__(self, app, *args, **kwargs):
        super().__init__(app, *args, **kwargs)

    def get(self, *args, **kwargs):
        return jsonify({})