import requests
from pprint import pprint as pp

def add_symbols(sm, symbols):
    for s in symbols:
        sm.register_symbol(s)

title_bar = lambda title='', rep=64: f' {title} '.rjust(1+rep//2 + len(title)//2, '=').ljust(rep, '=')
box = lambda text, title='', prefix='', rep=64: f'\n{rep*"=" if not title else title_bar(title, rep)}\n{prefix}{text}\n{rep*"="}\n'

def site_mapper(site_map):
        links = list(site_map.iter_rules())
        print(dir(links[0]))
        for l in links:
            print(l.endpoint, l.arguments, l.rule)

class TestSymbols:
    def test_symbols_get(self, server_symbols):
        url, sm, site_map = server_symbols

        resp = requests.get(url)
        print(box(dir(sm), f'test_symbols_get attributes', 'Attributes: '))
        print(box(sm.__dict__))

        site_mapper(site_map)
        assert True

    def test_symbols_add(self, server_symbols, symbol):
        url, sm, site_map = server_symbols
        symbols = []
        symbol_names = ['sym_a', 'sym_b', 'sym_c', 'sym_d']
        actor_names = ['act_a', 'act_b', 'act_c', 'act_d']
        for s, a in zip(symbol_names, actor_names):
            sym = symbol('Test symbols', s, a)
            symbols.append(sym)
            print(box(sym.variable, f'test_symbols_add generated symbol', f'{sym.module}: '))
        add_symbols(sm, symbols)
        print(box(dir(sm), f'test_symbols_add SymbolManager', f'{sm}: '))
        for sn in symbol_names:
            resp = requests.get(f'{url}/{sn}')
            print(box(resp.status_code, f'test_symbols_add {url}/{sn}', f'{sn}: '))
        site_mapper(site_map)
