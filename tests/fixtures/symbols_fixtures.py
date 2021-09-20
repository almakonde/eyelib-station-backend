'''
Symbols Fixtures

These are the fixtures necessary to run the symbols tests for station_backend.
'''
from pytest import fixture

from flask import Flask, url_for
from mjk_backend.threaded_server import ThreadedServer

from mjk_sim.environment import Environment, Actor
from station_common.implementation.sim.simulation import Symbol, create_symbol
from station_backend.views.symbols import SymbolManager

@fixture(scope='function')
def actor():
    return lambda actor_name: Actor(Environment(), name=actor_name)

@fixture(scope='function')
def symbol_symbols(actor):
    # return lambda module_name, symbol_name: Symbol(module_name, symbol_name, type_name='BOOL')
    return lambda module_name, symbol_name, actor_name: create_symbol(module_name, symbol_name, actor(actor_name), type_name='BOOL')


def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)
def site_map(app):
    links = []
    for rule in app.url_map.iter_rules():
        # Filter out rules we can't navigate to in a browser
        # and rules that require parameters
        if "GET" in rule.methods and has_no_empty_params(rule):
            url = url_for(rule.endpoint, **(rule.defaults or {}))
            links.append((url, rule.endpoint))
    # links is now a list of url, endpoint tuples

@fixture(scope='function')
def server_symbols():
    app = Flask("test_symbols")
    server = ThreadedServer(app, 'test')
    server.start()
    url = 'http://127.0.0.1:5000/symbols'
    symbol_manager = SymbolManager(app)
    yield url, symbol_manager, app.url_map
    server.shutdown()
    server.join()
