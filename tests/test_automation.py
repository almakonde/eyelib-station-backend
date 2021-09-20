import requests
from pprint import pprint as pp

def add_symbols(safety, symbols):
    for s in symbols:
        safety.add_symbol(s)

title_bar = lambda title='', rep=64: f' {title} '.rjust(1+rep//2 + len(title)//2, '=').ljust(rep, '=')
box = lambda text, title='', prefix='', rep=64: f'\n{rep*"=" if not title else title_bar(title, rep)}\n{prefix}{text}\n{rep*"="}\n'

class TestAutomation:
    def test_automation_get(self, server_safety):
        url, safety = server_safety

        resp = requests.get(url)
        assert not resp.json()
        attrs = (getattr(safety, symbol) for symbol in safety.notified_symbols)
        print(box(tuple(attrs), f'test_automation_add attributes'))
        assert not any(attrs)

    def test_automation_add(self, server_safety, symbol):
        url, safety = server_safety
        symbols = []
        for s in safety.notified_symbols:
            sym = symbol('Test safety', s)
            symbols.append(sym)
            print(box(sym.variable, f'test_automation_add generated symbol', f'{sym.module}: '))
        add_symbols(safety, symbols)
        resp = requests.get(url)
        print(box(resp.json(), f'test_automation_add RESP json (resp.json())'))

    def test_automation_change(self, server_safety):
        url, safety = server_safety

        for symbol in safety.notified_symbols:
            setattr(safety, symbol, True)
        resp = requests.get(url)
        print(box(resp.json(), f'test_automation_change RESP json (resp.json())'))
        print(box(resp.text, f'test_automation_change RESP text (resp.text)'))
        assert not resp.json()
        attrs = (getattr(safety, symbol) for symbol in safety.notified_symbols)
        print(box(tuple(attrs), f'test_automation_change attributes'))
        assert all(attrs)
