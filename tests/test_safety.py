import requests

from tests.utils import *

def add_symbols(safety, symbols):
    for s in symbols:
        safety.add_symbol(s)


class TestSafety:
    def test_safety_get(self, server_safety):
        url, safety = server_safety

        resp = requests.get(url)
        assert not resp.json()
        attrs = (getattr(safety, symbol, False) for symbol in safety.notified_symbols)
        print(box(tuple(attrs), f'test_safety_get', 'attributes: '))
        assert not any(attrs)

    def test_safety_add(self, server_safety, symbol_safety):
        url, safety = server_safety
        symbols = []
        for s in safety.notified_symbols:
            sym = symbol_safety('Test safety', s)
            symbols.append(sym)
            print(box(sym.variable, f'test_safety_add generated symbol', f'{sym.module}: '))
        add_symbols(safety, symbols)
        resp = requests.get(url)
        print(fox(resp.json(), f'test_safety_add RESP json (resp.json())'))

    def test_safety_change(self, server_safety):
        url, safety = server_safety

        for symbol in safety.notified_symbols:
            setattr(safety, symbol, True)
        resp = requests.get(url)
        print(fox(resp.json(), f'test_safety_change'))
        assert not resp.json()
        attrs = (getattr(safety, symbol, False) for symbol in safety.notified_symbols)
        print(box(tuple(attrs), f'test_safety_change', 'attributes: '))
        assert all(attrs)
