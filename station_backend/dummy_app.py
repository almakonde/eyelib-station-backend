import os
import sys
from flask import Flask, jsonify, send_from_directory, render_template, Response
from station_backend.settings import load as load_settings

from mjk_backend.shutdown import Shutdown

# settings = load_settings()

static_folder = os.path.abspath("../")

app = Flask(__name__,   static_url_path='',
                        static_folder=static_folder,
                        template_folder='web/templates')


Shutdown(app, 'shutdown')

@app.route('/')
def root():
    return jsonify({"yo":"yoyo"})
