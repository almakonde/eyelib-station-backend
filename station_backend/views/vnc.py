from flask import Blueprint, jsonify, request, Response
from mjk_vnc.vnc import VNCClient, FrameBuffer, Event
from mjk_backend.restful import Restful
from mjk_backend.stream import Stream

import threading
import PIL
import cv2
import time
import queue
from io import BytesIO

button_matching = {0: 1, 1:1, 2: 2, 4: 3, 'scrollup': 4, 'scrolldown': 5}

class VNCView(FrameBuffer, Restful, Stream):

    def __init__(self, app, *args, **kwargs):
        self._handlers = []
        self.lock = threading.Lock()
        self.data = None
        self.image = None
        self.width = 0
        self.height = 0
        
        name = kwargs.pop('name', 'vnc')
        FrameBuffer.__init__(self)
        Restful.__init__(self, app, name, **kwargs)
        Stream.__init__(self, app, path=self._path+'/stream', mimetype="multipart/x-mixed-replace; boundary=--frame", put_block=False)

    def update(self, x, y, w, h, data):
        new_image_needed = True if self.image is None else False

        self.data = data
        if self.image is not None:
            img_size = self.image.size
            if img_size[0] != w or img_size[1] != h:
                new_image_needed = True
        
        self.width = w
        self.height = h

        if new_image_needed:
            self.image = PIL.Image.frombytes('RGBA', (w, h), data)
        else:
            self.image.frombytes(data)

        encoded_image = BytesIO()
        self.image.convert('RGB').save(encoded_image, format='jpeg')
        self.push_item(encoded_image.getvalue())

    def register_event_handler(self, handler):
        if handler:
            self._handlers.append(handler)

    def unregister_event_handler(self, handler):
        if handler:
            self._handlers.remove(handler)

    def generate_item(self, item):
        return b'\r\n--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + item + b'\r\n'

    def _dispatch_event(self, event):
        for handler in self._handlers:
            handler.on_event(event)

    def get(self, *args, **kwargs):
        return jsonify([])
    
    def put(self, *args, **kwargs):
        front_event = request.json.get('event', None)
        if front_event:
            event_type = front_event.get('type', None)
            if event_type == 'click':
                m_event = Event(x=int(front_event['xp']*self.width), y=int(front_event['yp']*self.height), button=button_matching[front_event['button']], type='mouse_touch_down')
                self._dispatch_event(m_event)
                m_event = Event(x=int(front_event['xp']*self.width), y=int(front_event['yp']*self.height), button=button_matching[front_event['button']], type='mouse_touch_up')
                self._dispatch_event(m_event)
        return jsonify([])