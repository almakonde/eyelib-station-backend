from flask import Flask, jsonify, request, make_response
from station_common.automation.platform import PlatformAutomation
from station_common.automation.patient_station import PatientStationAutomation
from mjk_backend.restful import Restful

from station_common.automation.platform import logger


from station_backend import sse
import time
import requests

class AutomationAdjust:
    def __init__(self, psa: PatientStationAutomation):
        self.psa = psa
        self.epsilon = 0.5

        self.actions = {
            'left': ('InstrumentTable_Y', self.epsilon),
            'right': ('InstrumentTable_Y', -1.0*self.epsilon),
            'front': ('InstrumentTable_X', self.epsilon),
            'back': ('InstrumentTable_X', -1.0*self.epsilon),
            'cr_up': ('ChinRest', 2.0*self.epsilon),
            'cr_down': ('ChinRest', -2.0*self.epsilon),
            'station_up': ('StationHeight', 10.0*self.epsilon),
            'station_down': ('StationHeight', -10.0*self.epsilon)
        }

    def adjust(self, action) -> bool:
        ret = False        
        if self.psa:
            if action:
                axis, increment = self.actions.get(action, (None, 0.0))
                if axis is not None:
                    logger.info("adjust: %s by %f",axis,increment)
                    resume = (self.psa.running_state == "running")
                    self.psa.pause()
                    if axis == 'StationHeight':
                        self.psa.patient_station.sh_axes[axis].move_by_mm(increment)
                    else:
                        self.psa.patient_station.axes[axis].move_by_mm(increment)
                    if resume:
                        self.psa.resume()
                    ret = True
        return ret


class AutomationView(Restful):

    def __init__(self, app: Flask, psa: PatientStationAutomation):
        super().__init__(app, 'automation')
        self.psa = psa
        self.automation_adjust = AutomationAdjust(psa)
        self.commands = {
            'start': self.start,
            'stop': self.stop,
            'pause': self.pause,
            'resume': self.resume,
            'emergency': self.emergency,
            'switch_program': self.switch_program,
            'state': self.state,
            'show': self.show,
            'adjust': self.adjust,
            'adjustment_done': self.adjustment_done,
            'disable_patient_validation': self.disable_patient_validation,
            'relaunch_vx120_automation': self.relaunch_vx120_automation,
            'move_vx120_left': self.move_vx120_left,
            'relaunch_revo_automation': self.relaunch_revo_automation,
            'move_revo_right': self.move_revo_right,
            'shutdown_instruments': self.shutdown_instruments,
            'reset_instruments': self.reset_instruments
        }

        self.psa.bind('recursive_state_str', self.on_state_changed)
        self.psa.bind('progress', self.on_progress_changed)
        self.psa.bind('running_state', self.on_running_changed)

        self._variables = {
            'state': lambda: self.psa.recursive_state_str,
            'bstate': lambda: self.psa.state.name,
            'programs': list(self.psa.programs.keys()),
            'program': lambda: self.psa.current_program,
            'running': lambda: self.psa.running_state,
            'progress': lambda: self.psa.progress,
            'error': lambda: (self.psa.namespace.error, self.psa.namespace.error_msg)
        }
        app.add_url_rule('/automation/<variable>', 'variables', self._get_variable)

    def _variable_val(self, variable):
        value = self._variables.get(variable, None)
        if value is not None:
            if callable(value):
                return value()
            else:
                return value
        else:
            return None

    def _variables_val(self):
        return {variable: self._variable_val(variable) for variable in self._variables.keys()}

    def _get_variable(self, variable):
        value = self._variable_val(variable)
        if value is not None:
            return jsonify({'value': value})
        else:
            return make_response('variable not found', 500)

    def get(self, *args, **kwargs):
        if request.is_json:
            command = request.json.get('command', 'show')
        else:
            command = request.args.get('command', 'show')

        if request.is_json:
            data = request.json.get('data', None)
        else:
            data = request.args.get('data', None)

        if command in self.commands.keys():
            return self.commands[command](data)
        else:
            return make_response('command not found', 500)

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

    def state(self, *args, **kwargs):
        return jsonify({'state': self.psa.state.name, 'recursive':self.psa.recursive_state_str})

    def emergency(self, *args, **kwargs):
        self.psa.emergency()
        return jsonify({})

    def start(self, *args, **kwargs):
        self.psa.namespace.do_init = True
        self.psa.start()
        return jsonify({})

    def stop(self, *args, **kwargs):
        self.psa.stop()
        return jsonify({})

    def pause(self, *args, **kwargs):
        self.psa.pause()
        return jsonify({})

    def resume(self, *args, **kwargs):
        self.psa.resume()
        return jsonify({})
    
    def restart(self, *args, **kwargs):
        self.psa.restart()
        return jsonify({})

    def cancel(self, *args, **kwargs):
        self.psa.cancel()
        return jsonify({})

    def adjustment_done(self, *args, **kwargs):
        self.psa.adjustment_done()
        self.log_total_adjustments()
        return jsonify({})

    def log_total_adjustments(self):
        '''
            Logs the total adjustments done for the patient.
        '''
        id = self.psa.patient_station.examination['patient_id']
        sitting_down = self.psa.patient_station.examination['morphology']['sit_down_flag']
        if sitting_down:
            previous_station_height = self.psa.patient_station.examination['morphology']['sit_down_height']
        else:
            previous_station_height = self.psa.patient_station.examination['morphology']['chin_z']
        station_height_diff = round(self.psa.chin_z_from_station_height()) - previous_station_height
        previous_chin_rest_height = round(self.psa.chin_to_eyeline_max() - self.psa.patient_station.examination['morphology']['chin_to_eyeline'])
        chin_rest_dif = round(self.psa.chinrest_z()) - previous_chin_rest_height
        logger.info(f"Total adjustment for patient ID : {id}, station height : {station_height_diff} (new height : {round(self.psa.chin_z_from_station_height())}, previous : {previous_station_height}) and chin rest : {chin_rest_dif} (new height : {round(self.psa.chinrest_z())}, previous : {previous_chin_rest_height}). Sitting down : {sitting_down}")

    def disable_patient_validation(self, *args, **kwargs):
        self.psa.disable_patient_validation()
        return jsonify({})

    def switch_program(self, *args, **kwargs):
        if len(args) > 0:
            program = args[0]
            self.psa.switch_program(program)
        return jsonify({'current_program': self.psa.current_program})

    def show(self, *args, **kwargs):
        return jsonify(self._variables_val())

    def relaunch_vx120_automation(self, *args, **kwargs):
        '''
            Sends a GET request to the VX120 that triggers a shutdown.
        '''
        vx120_params = self.psa.patient_station.platform.instrument_storage.instruments_parameters['VX120-01']['ruia']
        path = f"http://{vx120_params['rest_host']}:{(vx120_params['rest_port'])}/shutdown"
        ret = requests.get(path)
        return make_response("success" if ret else "Relaunching VX120 failed", 200 if ret else 500)

    def move_vx120_left(self, *args, **kwargs):
        '''
            Propagates the command to move the VX120 to station_common.
        '''
        ret = self.psa.move_instrument_head('VX120')
        logger.info('In automation.py calling move_instrument_head for VX120')
        return make_response("success" if ret else "moving VX120 failed", 200 if ret else 500)

    def relaunch_revo_automation(self, *args, **kwargs):
        '''
            Sends a GET request to the REVO that triggers a shutdown.
            This makes the REVO automation restart because it has a parameter that makes
            it automatically restart.
        '''
        revo_params = self.psa.patient_station.platform.instrument_storage.instruments_parameters['REVO-01']['ruia']
        path = f"http://{revo_params['rest_host']}:{(revo_params['rest_port'])}/shutdown"
        ret = requests.get(path)
        return make_response("success" if ret else "Relaunching RVO failed", 200 if ret else 500)

    def move_revo_right(self, *args, **kwargs):
        '''
            Propagates the command to move the REVO to station_common.
        '''
        ret = self.psa.move_instrument_head('REVO')
        logger.info('In automation.py calling move_instrument_head for REVO')
        return make_response("success" if ret else "moving REVO failed", 200 if ret else 500)        

    def shutdown_instruments(self, *args, **kwargs):
        '''
            Propagates the command to shutdown the instruments.
        '''        
        logger.info('In automation.py caling shutdown_instruments')
        ret = self.psa.instrument_shutdown()
        return make_response("success" if ret else "shutdown instruments failed", 200 if ret else 500)    


    def reset_instruments(self, *args, **kwargs):
        '''
            Propagates the command to reset the instruments.
        '''        
        logger.info('In automation.py caling reset_instruments')
        ret = self.psa.instrument_reset()
        return make_response("success" if ret else "reset instruments failed", 200 if ret else 500)     

    def adjust(self, *args, **kwargs):
        ret = False
        if len(args) > 0:
            action = args[0]
            ret = self.automation_adjust.adjust(action)
        return make_response("success" if ret else "action ["+action+"] failed", 200 if ret else 500)

    def on_state_changed(self, *argv):
        timestamp = time.time()
        event = '/automation/state'
        data = {
                'type': 'automation',
                'path': 'automation/state',
                'name': 'state',
                'timestamp': timestamp,
                'value': self.psa.recursive_state_str
                    }
        sse.push_event(event, data)
    
    def on_progress_changed(self, *argv):
        timestamp = time.time()
        event = '/automation/progress'
        data = {
                'type': 'automation',
                'path': 'automation/progress',
                'name': 'progress',
                'timestamp': timestamp,
                'value': self.psa.progress
                    }
        sse.push_event(event, data)


    def on_running_changed(self, *argv):
        timestamp = time.time()
        event = '/automation/running'
        data = {
                'type': 'automation',
                'path': 'automation/running',
                'name': 'state',
                'timestamp': timestamp,
                'value': self.psa.running_state
                    }
        sse.push_event(event, data)
