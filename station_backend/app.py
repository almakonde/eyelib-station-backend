from flask import Flask, jsonify, send_from_directory, render_template, Response
from flask_cors import CORS

from station_backend.views.login import LoginView
from station_backend.views.logout import LogoutView
from station_backend.views.symbols import SymbolManager
from station_backend.views.axes import AxesView, SHAxesView
from station_backend.views.automation import AutomationView
from station_backend.views.examinations import ExaminationsView
from station_backend.views.instruments import InstrumentsView
from station_backend.views.manual_mode import ManualModeView
from station_backend.views.pwr import PowerView
from station_backend.views.waypoints import PatientStationWaypointsView
from station_backend.views.teaching import PatientStationTeachingView
from station_backend.views.persistence import PersistenceView
from station_backend.views.safety import SafetyView
from station_backend.views.patient_adjust import PatientAdjustView
from station_backend.views.station import StationView
from station_backend.views.simulation import SimulationView
from station_backend.views.simulation_bc import SimulationBackCamera
from station_backend.views.side_cameras import SideCamerasView


from station_backend.settings import load as load_settings

from mjk_utils.cmd import script_dir
from mjk_utils.logging import Logging
from mjk_vnc.vnc import vnc_clean
from mjk_backend.shutdown import Shutdown
from mjk_backend.alive import Alive


from station_common.automation.platform import PlatformAutomation
from station_common.automation.patient_station import PatientStationAutomation

from mjk_utils.speech_reactor import SpeechReactor
from station_common.events_log import register_events_logger

from mjk_utils.workers import WorkerPool


from station_backend import sse
from station_backend import version, version_backend
from station_common import version as version_common
from mjk_ads import version as version_mjk_ads
from mjk_backend import version as version_mjk_backend
from mjk_common import version as version_mjk_common
from mjk_ruia import version as version_mjk_ruia
from mjk_sim import version as version_mjk_sim
from mjk_utils import version as version_mjk_utils
from mjk_vision import version as version_mjk_vision
from mjk_vnc import version as version_mjk_vnc
from mjk_vnc_backend import version as version_mjk_vnc_backend
from eyelib_logger import version as version_eyelib_logger

import os, sys

import atexit

import time


from station_common.implementation.sim.simulation import SimConnection, Simulation
from station_common.implementation.sim.gen2 import gen2_simulation
from station_common.platform import EyeLibPlatform
from station_common.connection import connection_factory

import logging

logger = logging.getLogger('main_app')
logger.setLevel(logging.INFO)


settings = load_settings()

# template_folder = os.path.realpath(script_dir()+'/../../station-frontend/station/dist')
static_folder = os.path.abspath(settings.staticFolder)

app = Flask(__name__,   static_url_path='',
                        static_folder=static_folder,
                        template_folder='web/templates')

app.secret_key = 'b3\\x81\\x1e9\\x9d\\xd0H]!})\\xf9F\\xefU\\xd8\\xf9\\x99\\x023[\\xd4%0'
app.__version__ = version.VERSION_STRING
app.subversions = {'Backend': version_backend.VERSION_STRING,
                    'Common': version_common.VERSION_STRING,
                    'Eyelib Logger': version_eyelib_logger.VERSION_STRING,
                    'mjk-ads': version_mjk_ads.VERSION_STRING,
                    'mjk-backend': version_mjk_backend.VERSION_STRING,
                    'mjk-common': version_mjk_common.VERSION_STRING,
                    'mjk-ruia': version_mjk_ruia.VERSION_STRING,
                    'mjk-sim': version_mjk_sim.VERSION_STRING,
                    'mjk-utils': version_mjk_utils.VERSION_STRING,
                    'mjk-vision': version_mjk_vision.VERSION_STRING,
                    'mjk-vnc': version_mjk_vnc.VERSION_STRING,
                    'mjk-vnc-backend': version_mjk_vnc_backend.VERSION_STRING}
app.language = settings.language

try:
    wp = WorkerPool('default', settings.workerPoolSize)
except:
    wp = None

#Supports Credentials is required for cookie reading
CORS(app, supports_credentials=True)
Shutdown(app, 'shutdown')
Alive(app, 'alive')
sse.Sse(app)

@app.route('/')
def root():
    return app.send_static_file('index.html')


def app_cleanup():
    print("Cleaning up")
    if con is not None:
        con.close()
        platform.on_connection_closed(con)
        if examination_view is not None:
            examination_view.stop()

    vnc_clean()

    if wp is not None:
        wp.terminate()

    if settings.simulation:
        sim0.stop_realtime()



#Setting login & logout - TODO : Mikael can put this where he wants
login_view = LoginView(app)
logout_view = LogoutView(app)

if settings.simulation:
    sim0 = gen2_simulation("sim0")
    addr = "sim0"
    
else:
    addr = settings.stationAddress

con = connection_factory(addr)
atexit.register(app_cleanup)

symbol_manager = SymbolManager(app)

persistence_filename = os.path.realpath(script_dir()+'/../' + addr.replace(':', '_') + '.xml')
persistence = PersistenceView(app, path=persistence_filename)

if con:
    con.open()
    if con.is_open:
        # persistence_filename = os.path.realpath(script_dir()+'/../' + addr.replace(':', '_') + '.xml')
        # try:
        #     Persistence().from_file(persistence_filename)
        # except:
        #     print("Failed to load persistence data from file "+persistence_filename)

        if not persistence.load():
                print("Failed to load persistence data from file "+persistence_filename)

        platform = EyeLibPlatform([con])
        if platform:
            platform.populate()


            station = platform.patient_stations.get('PS1', None)
            if station:
                axes = station.axes
                sh_axes = station.sh_axes

                station.init() # pwr to the trays

                examination_view = ExaminationsView(app, station._exs)


                Logging().setup(settings.logging_url)
                register_events_logger(station.events)
                voice = SpeechReactor(station.patient_interaction)
                
                voice.load(script_dir()+"/voices_"+app.language+".json")
                station.events.start()

                power_view = PowerView(app, pwr=station.pwr)

                if settings.simulation:
                    logger.info("Application type: SIMULATION")
                    simulation_view = SimulationView(app, sim0)

                    simulation_view._put_timescaling(5)

                    vx120 = platform.instrument_storage.get_instrument_from_iid('VX120-01')
                    revo = platform.instrument_storage.get_instrument_from_iid('REVO-01')

                    bc_sim = SimulationBackCamera(app, station, path="/bc_sim")
                else:
                    logger.info("Application type: REAL STATION")
                    logger.info("STATION: %s", addr)
                
                axes_view = AxesView(app, station)
                sh_axes_view = SHAxesView(app, station)

                pa = PlatformAutomation(platform)
                if pa is not None:
                    psa = pa.psas[station]
                    if psa is not None:
                        semiauto_view = PatientStationWaypointsView(app, psa)
                        automation_view = AutomationView(app, psa)
                        patient_adjust_view = PatientAdjustView(app, psa)
                        teaching_view = PatientStationTeachingView(app, psa)
                        instruments_view = InstrumentsView(app, platform, station, psa)
                        manual_mode_view = ManualModeView(app, platform, station, psa)
                        side_cameras_view = SideCamerasView(app, platform, station, psa)
                        station_view = StationView(app, psa)
                        ''' Generate all programs state diagrams'''
                        # for filtered in [False, True]:                       
                        #     for prog in psa.programs.keys():
                        #         psa.switch_program(prog)
                        #         filtered_target_states = []
                        #         if filtered:
                        #             filtered_target_states = ['fault']
                        #             if prog in ['default_automation', 'one_instrument_exam']:
                        #                 filtered_target_states.append('restart')
                        #         filtered_text = ''
                        #         if len(filtered_target_states)>0:
                        #             filtered_text = '_filtered'
                        #         with open('state_diagram_'+psa.current_program+filtered_text+'.wsd', 'w') as f:
                        #             f.write(psa.get_plant_uml(psa.current_program, filtered_target_states))
                        ''' END of Generate all programs state diagrams'''
                    if settings.autoinit:
                        pa.start()
                for axis_name, axis in axes.items():
                    for symbol in axis.symbols.values():
                        path = "/"+axis_name+"/"+symbol.variable
                        logger.info("registering %s ", path)
                        symbol_manager.register_symbol(symbol, path=path)

                for axis_name, axis in sh_axes.items():
                    for symbol in axis.symbols.values():
                        path = "/"+axis_name+"/"+symbol.variable
                        logger.info("registering %s ", path)
                        symbol_manager.register_symbol(symbol, path=path)

                for symbol in station.safety.symbols.values():
                    path = "/safety/"+symbol.variable
                    logger.info("registering %s ", path)
                    symbol_manager.register_symbol(symbol, path=path)

                for pwr_switch in station.pwr.pwr_sws.values():
                    path = "/pwr/"+pwr_switch.symbol.variable
                    logger.info("registering %s ", path)
                    symbol_manager.register_symbol(pwr_switch.symbol, path=path)


                SafetyView(app, station.safety)
                
                time.sleep(2)

                platform.initialize_instruments()
                

