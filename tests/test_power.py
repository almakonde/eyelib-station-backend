import requests
from pprint import pprint as pp

def add_symbols(safety, symbols):
    for s in symbols:
        safety.add_symbol(s)

title_bar = lambda title='', rep=64: f' {title} '.rjust(1+rep//2 + len(title)//2, '=').ljust(rep, '=')
box = lambda text, title='', prefix='', rep=64: f'\n{rep*"=" if not title else title_bar(title, rep)}\n{prefix}{text}\n{rep*"="}\n'

class TestPower:
    def test_power_get(self, server_power):
        url = server_power

        resp = requests.get(url)
        print(box(resp.raw.data, f'test_power_add {url}', f'{resp.status_code}: '))

    def test_power_add(self, server_power):
        url = server_power
        resp = requests.put(url, data = {'pwr_id': 'on'})
        print(box(resp.json(), f'test_power_add RESP json (resp.json())'))

