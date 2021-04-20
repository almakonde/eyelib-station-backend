from mjk_backend.restful import Restful
from flask import Flask, jsonify, request, make_response
from station_common.automation.patient_station import PatientStationAutomation
from station_common.teaching import Teaching, TaughtAxes, TaughtPoint
import json
from station_backend.utilities.decoraters import roles_required

class PatientStationTeachingView(Restful):

    def __init__(self, app, psa: PatientStationAutomation, **kwargs):
        super().__init__(app, name="teaching", **kwargs)
        self.psa = psa
        self._commands = {
                        'goto': self._goto,
                        'teach': self._teach,
                        'teach_all': self._teach_all
                        }

    def _set_from_taught(self, taught):
        return {
                'axes': {axis_id:axis.name for axis_id, axis in taught.axes.items()},
                'points': {point_id: {aid: axes_values.get(aid, 0.0) for aid in taught.axes.keys()} for point_id, axes_values in taught.taught_points.items()}
            }

    @roles_required("stationFrontendAllowed")
    def get(self, *args, **kwargs):

        if request.is_json:
            command = request.json.get('command', None)
            data = request.json.get('data', None)
        else:
            command = request.args.get('command', None)
            dstr = request.args.get('data', None)            
            data = json.loads(dstr) if dstr is not None else None

        if command is None:
            ret = {}
            for taught in Teaching().taught:
                ret[taught.name] = self._set_from_taught(taught)
                # data[taught.name] = {
                #     'axes': {axis_id:axis.name for axis_id, axis in taught.axes.items()},
                #     'points': {point_id: {aid: axes_values.get(aid, 0.0) for aid in taught.axes.keys()} for point_id, axes_values in taught.taught_points.items()}
                # }
            return jsonify(ret)
        else:
            if command == 'get_values':
                set_id = data.get('set', None)
                point_id = data.get('point', None)
                if set_id is not None and point_id is not None:
                    taught = Teaching().get(set_id, None)
                    if taught is not None:
                        return taught.taught_points.get(point_id)
                return make_response("failed to find values", 500)
            if command == 'get_set':
                set_id = data.get('set', None)
                
                if set_id is not None:
                    taught = Teaching().get(set_id, None)
                    if taught is not None:
                        ret = self._set_from_taught(taught)
                        return jsonify(ret)
                return make_response("failed to find values", 500)

    @roles_required("stationFrontendAllowed")
    def put(self, *args, **kwargs):
        ret = False
        command = request.json.get('command', None)
        if command is not None:
            data = request.json.get('data')
            if command in self._commands.keys():
                ret = self._commands[command](data)
        if ret is not None:
            return jsonify(ret)
        else:
            return make_response("command failed", 500)

    @roles_required("stationFrontendAllowed")
    def _goto(self, data):
        ret = None
        taught_name = data.get('set', None)
        taught_point_id = data.get('point', None)
        if (taught_name is not None) and (taught_point_id is not None):
            taught = Teaching().get(taught_name)
            if taught is not None:
                taught.goto(taught_point_id)
                ret = True
        return ret

    @roles_required("stationFrontendAllowed")
    def _teach(self, data):
        ret = None
        taught_name = data.get('set', None)
        taught_point_id = data.get('point', None)
        taught_axis_id = data.get('axis', None)
        if (taught_name is not None) and (taught_point_id is not None) and (taught_axis_id is not None):
            taught = Teaching().get(taught_name)
            if taught is not None:
                taught.teach(taught_point_id, taught_axis_id)
                ret = True
        return ret

    @roles_required("stationFrontendAllowed")
    def _teach_all(self, data):
        ret = None
        taught_name = data.get('set', None)
        taught_point_id = data.get('point', None)

        if (taught_name is not None) and (taught_point_id is not None):
            taught = Teaching().get(taught_name)
            if taught is not None:
                for axis_id in taught.axes.keys():
                    taught.teach(taught_point_id, axis_id)
                ret = True
        return ret
