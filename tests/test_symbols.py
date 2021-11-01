import requests

from tests.utils import *

def add_symbols(sm, symbols):
    for s in symbols:
        sm.register_symbol(s, path=f'/test/{s.variable}')

def site_mapper(site_map):
        links = list(site_map.iter_rules())
        # print(fox(dir(links[0]), 'site_mapper'))
        for l in links:
            print(f'Endpoint: {l.endpoint}\targs: {l.arguments}\trule: {l.rule}')

class TestSymbols:
    def test_symbols_get(self, server_symbols):
        url, sm, site_map = server_symbols
        resp = requests.get(url)
        print(fox(resp, f'test_symbols_get attributes', 'resp: '))
        print(fox(sm.__dict__, f'test_symbols_get attributes', '__dict__: '))
        site_mapper(site_map)
        assert True

    def test_symbols_add(self, server_symbols, symbol_symbols):
        url, sm, site_map = server_symbols
        symbols = []
        symbol_names = ['sym_a', 'sym_b', 'sym_c', 'sym_d']
        actor_names = ['act_a', 'act_b', 'act_c', 'act_d']
        # for s, a in zip(symbol_names, actor_names):
        for s, a in [(f'sym_{l}', f'act_{l}') for l in 'abcd']:
            sym = symbol_symbols('Test symbols', s, a)
            symbols.append(sym)
            print(fox(sym.variable, f'test_symbols_add generated symbol', f'{sym.module}: '))
        add_symbols(sm, symbols)
        # print(fox(dir(sm), f'test_symbols_add SymbolManager', f'{sm}: '))
        url = 'http://127.0.0.1:5000/test'
        for sn in symbol_names:
            resp = requests.get(f'{url}/{sn}')
            print(box((resp.status_code, resp.text), f'test_symbols_add {url}/{sn}', f'{sn}: '))
        site_mapper(site_map)
