from flask import Response
# from collections import deque
import queue
import json
import time

from mjk_utils.singleton import SingletonDecorator
from mjk_backend.stream import Stream

@SingletonDecorator
class Sse(Stream):

    def __init__(self, app):
        super().__init__(app, path='/sse', stream_queue_size=1000, put_block=False)
        # self._queue = queue.Queue(maxsize=10000)
        # app.add_url_rule('/sse', '/sse', self.stream)

    # def register_event(event):
        # self._events.append(event)

    def push_event(self, event, data):
        self.push_item({'event': event, 'data': data})
        # self._queue.put_nowait({'event': event, 'data': data})
        # print(_queue.qsize())

    def generate_item(self, item):
        # print('fetch event: '+item['event'])
        return 'event:'+item['event']+'\ndata:'+json.dumps(item)+'\n\n'

    # def generate(self):
    #     while True:
    #         time.sleep(0.01)
    #         item = self._queue.get(block=True)
    #         if item:
    #             print('fetch event: '+item['event'])
    #             yield 'event:'+item['event']+'\ndata:'+json.dumps(item)+'\n\n'


    # def stream(self):
    #     # def eventStream():
    #     #     while True:
    #     #         time.sleep(0.01)
    #     #         item = _queue.get(block=True)
    #     #         if item:
    #     #             # event = item.get('event', '')
    #     #             # data = item.get('data', '')
    #     #                 yield 'event:'+item['event']+'\ndata:'+json.dumps(item)+'\n\n'
    #     #             # "data:{'event': event, 'data': data}"
        
    #     return Response(self.generate(), mimetype="text/event-stream")


def push_event(event, data):
    Sse().push_event(event, data)
 
def push(event_type: str, name: str, value):
        timestamp = time.time()
        event = '/%s/%s' % (event_type, name)
        data = {
                'type': event_type,
                'path': '/%s/%s' % (event_type, name) ,
                'name': name,
                'timestamp': timestamp,
                'value': value
                    }        
        push_event(event, data)

