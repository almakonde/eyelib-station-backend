from flask import Flask, request, Response, jsonify
from queue import Queue
from functools import partial
import time
import json
import numbers

from mjk_backend.restful import Restful

from station_backend import sse
from ..backend_logging import logger as b_logger


def strboolparse(s):
    if isinstance(s, numbers.Number):
        return bool(s)
    elif isinstance(s, str):
        return s.lower() in ['true', '1', 'y', 'yes', 'on']
    else:
        return s

symbol_typemap = {
    'LREAL': float,
    'INT': int,
    'BOOL': strboolparse
}

def symbol_cast(symbol, value):
    if hasattr(symbol, "typeName"):
        return symbol_typemap.get(symbol.typeName, str)(value)
    else:
        return value



class RESTfulSymbol(Restful):
    def __init__(self, symbol, app, path):
        self.symbol = symbol
        super().__init__(app, path, path=path)

    def get(self, *args, **kwargs):
        try:
            ret = jsonify({'value': self.symbol.read()})
        except TypeError:
            data = self.symbol.read()
            if hasattr(data, "value"):
                ret = jsonify({'value': data.value})
            else:
                ret = jsonify({'value': str(data)})
        return ret

    def put(self, *args, **kwargs):
        value = request.json.get('value', None)
        b_logger.info("PUT: " + json.dumps({'path':self._path, 'value':value}))     
        if value is not None:
            self.symbol.write(symbol_cast(self.symbol, value))            
        return self.get()

    def post(self, *args, **kwargs):
        if 'value' in request.args:
            self.symbol.write(symbol_cast(self.symbol, (request.args['value'])))
        return self.get()


class SymbolManager:

    def __init__(self, app: Flask, path='/symbols'):
        self.app = app
        self.symbols_per_path = {}
        self.symbols_per_name = {}
        self.path_from_symbol = {}
        self.symbol_restful = {}
        self.path = path
        self.app.add_url_rule(self.path, 'symbols', self.restful, methods=['GET', 'PUT'])
        # self.app.add_url_rule(self.path+'/events', 'events', self.stream)
        self.symbol_events = Queue()
        self.dummy_value = 0

    def restful(self):
        if request.method == 'GET':
            return self.get()
        if request.method == 'PUT':
            return self.put()

    def register_symbol(self, symbol, **kwargs):
        if symbol:
            path = kwargs.get('path', self.path+'/'+symbol.variable)
            self.symbol_restful[symbol] = RESTfulSymbol(symbol, self.app, path)
            self.symbols_per_path[path] = symbol
            self.symbols_per_name[symbol.variable] = symbol
            self.path_from_symbol[symbol] = path
            # self.app.add_url_rule(path, path, self.symbol_restful[symbol].restful, methods=['GET', 'PUT', 'POST'])
            try:
                symbol.add_device_notification(partial(self.on_symbol_event, symbol))
            except:
                print("FAILED TO REGISTER SYMBOL: "+path)
            # symbol.add_device_notification(self.on_dummy)

    def on_dummy(self, *args, **kwargs):
        print("DUMMY")

    def unregister_symbol(self, symbol):
        if symbol:
            del self.symbol_restful[symbol]
            del self.path_from_symbol[symbol]
            del self.symbols_per_name[symbol.variable]
            del_keys = [k for k, v in self.symbols_per_path.items() if v == symbol]
            for k in del_keys:
                del self.symbols_per_path[k]

    def on_symbol_event(self, symbol, timestamp, value):
        if isinstance(value, numbers.Number):
            # print('number')
            valid_value = value
        else:
            if hasattr(value, 'value'):
                valid_value = value.value
            else:
                valid_value = str(value)

        event = self.path_from_symbol[symbol]
        data = {
                'type': 'symbol',
                'path': self.path_from_symbol[symbol],
                'name': symbol.variable,
                'timestamp': timestamp,
                'value': valid_value
                } 
        # b_logger.info("push to sse: "+json.dumps({'path':data.get('path'), 'value':data.get('value')}))  
        sse.push_event(event, data)
        
        # self.symbol_events.put(event)

    def get(self, *args, **kwargs):
        print(args)
    
    def put(self, *args, **kwargs):
        print(args)

    def put_dummy_event(self):
        event = {
                    'type': 'event',
                    'data': {
                            'type': 'symbol',
                            'path': self.path+'/dummy',
                            'name': 'dummy',
                            'timestamp': time.time(),
                            'value': self.dummy_value
                            }
                }
        # self.symbol_events.put(event)
        self.dummy_value += 1
    
    # def generate(self):
    #     while True:
    #         time.sleep(0.01)
    #         event = self.symbol_events.get(block=True)
    #         if event:
    #             yield('data:'+json.dumps(event)+'\n\n')

    # def stream(self):
    #     return Response(self.generate(), mimetype="text/event-stream")
    




        
