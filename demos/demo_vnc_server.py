from station_backend.views.vnc import VNCClient, VNCView
from mjk_backend.threaded_server import ThreadedServer
from flask import Flask
from flask_cors import CORS
from PIL import Image
import time

app = Flask("vnc")

CORS(app)

viewer = VNCView(app)
client = VNCClient("192.168.11.123", 5900, "MjkAdm", viewer)

client.start()

while not client.connected:
    time.sleep(1)
viewer.register_event_handler(client)

# app.add_url_rule('/yop', 'yop', viewer.restful, methods=['GET', 'PUT'])
# app.add_url_rule('/video_stream', 'video_stream', viewer.stream)

# server = ThreadedServer(app, 'test', port=5003)
# server.start()
# server.join()

app.run(port=5003)