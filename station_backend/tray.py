import os
import requests
import subprocess

from infi.systray import SysTrayIcon
from mjk_utils.cmd import script_dir
from station_backend.settings import load as load_settings
from mjk_utils.logging import Logging
from backend_logging import logger as b_logger

from multiprocessing import Event

import io
import sys
old_stdout = sys.stdout
log_filename = "station-backend.log"
log_filepath = os.path.abspath(log_filename)
# log_file = open(log_filename, "w")
sys.stdout = io.TextIOWrapper(open(log_filename, 'wb', 0), write_through=True)
sys.stderr = io.TextIOWrapper(open(log_filename, 'wb', 0), write_through=True)

autorestart_filepath = os.path.join(script_dir(), "autorestart")

force_exit = Event()

def appp(con):

    sys.stdout = io.TextIOWrapper(open(log_filename, 'wb', 0), write_through=True)
    sys.stderr = io.TextIOWrapper(open(log_filename, 'wb', 0), write_through=True)

    try:
        from app import app, settings, app_cleanup
        from backend_logging import logger
        con.send("starting")
    
        app.run(host=settings.host, port=settings.port, threaded=True)
        con.send("terminated")
        logger.info("Application ended nominally")
    except Exception as excep:
        con.send("crashed")
        logger.error("Application failed with exception %s" % (str(excep)))


p = None

def _menu_shutdown(systray):
    requests.get("http://127.0.0.1:5003/shutdown")

def _menu_showlog(systray):
    subprocess.run(["notepad.exe", log_filepath])

def _menu_kill(systray):
    if isinstance(p, Process):
        p.terminate()

def _exit_callback(systray):
    force_exit.set()
    _menu_shutdown(systray)

# def _menu_autorestart_toggle(systray):
#     autorestart = os.path.isfile(autorestart_filepath)
#     if autorestart:
#         pass # delete autorestart file
#     else:
#         pass #create autorestart file

# log_filename = "station-backend.log"


icon_path = os.path.join(script_dir(), "icon.ico")

supported_colors = ['green', 'cyan', 'red', 'white']

icons_paths = { color: os.path.join(script_dir(), "icon_%s.ico" % color) for color in supported_colors}


def update_icon(systray: SysTrayIcon, color):
    icon_path = icons_paths.get(color, None)
    if icon_path is not None:
        systray.update(icon_path)

status_colors = { 'starting': 'green', 'crashed': 'red', 'terminated': 'white'}

if __name__ == '__main__':

    menu_options = (("shutdown", None, _menu_shutdown), ("show local log", None, _menu_showlog),)

    systray = SysTrayIcon(icon_path, "Eyelib Station", menu_options, on_quit=_exit_callback)

    systray.start()

    from multiprocessing import Process, Pipe

    settings = load_settings()
    Logging().setup(settings.logging_url)

    

    autorestart = True
    while(autorestart):
        # autorestart = os.path.isfile(autorestart_filepath) and (not force_exit.is_set())
        autorestart = settings.autoRestart and (not force_exit.is_set())
        b_logger.info("Starting backend (autorestart: %s)" % str(autorestart))
        parent_con, child_con = Pipe(duplex=True)
        p = Process(target=appp, args=(child_con,))
        if p is not None:
            p.start()
            update_icon(systray, 'cyan')
            running = True
            while(running):
                p.join(timeout=0.1)
                if parent_con.poll(timeout=0.3):
                    status = parent_con.recv()
                    color = status_colors.get(status, None)
                    if color is not None:
                        update_icon(systray, color)
                
                
                running = (p.exitcode is None)
        # autorestart = os.path.isfile(autorestart_filepath) and (not force_exit.is_set())
        autorestart = settings.autoRestart and (not force_exit.is_set())

    systray.shutdown()
    exit(1)