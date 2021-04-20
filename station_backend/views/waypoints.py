from mjk_backend.restful import Restful
from flask import Flask, jsonify, request, make_response
from station_common.automation.patient_station import PatientStationAutomation
from station_backend import sse
from mjk_utils.workers import defer
from station_backend.utilities.decoraters import roles_required

class PatientStationWaypointsView(Restful):

    def __init__(self, app, psa: PatientStationAutomation, **kwargs):
        super().__init__(app, name="waypoints", **kwargs)
        self.psa = psa

    @roles_required("stationFrontendAllowed")
    def get(self, *args, **kwargs):
        points = [point.name for point in self.psa.namespace.points.values()]
        return jsonify(points)

    @roles_required("stationFrontendAllowed")
    def put(self, *args, **kwargs):
        command = request.json.get('command', None)
        if command is not None:
            data = request.json.get('data')
            if command == 'reach':
                point = self.psa.namespace.points.get(data, None)
                if point:
                    point.goto()
                    return jsonify({})
                else:
                    return make_response('point not found', 500)
            elif command == "reachwait":
                point = self.psa.namespace.points.get(data, None)
                if point:
                    defer(point.wait, callback=self.on_event)
                    return jsonify({})
                else:
                    return make_response('point not found', 500)
            elif command == 'is_reached':
                point = self.psa.namespace.points.get(data, None)
                if point:
                    is_reached = point.reached()
                    return jsonify({'is_reached':is_reached})
                else:
                    return make_response('point not found', 500)
            else:
                return make_response('command not found', 500)
        else:
            return make_response('command not found', 500)

    @roles_required("stationFrontendAllowed")
    def on_event(self, *args, **kwargs):
        # print(args)
        worker_status = args[0]
        name = worker_status.data.get('point', 'unknown')
        if name != 'unknown':
            status={
                'progress':worker_status.progress,
                'reached':worker_status.data['reached']
            }
            sse.push('waypoints', name, status)
