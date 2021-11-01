import requests

from tests.utils import *

def add_symbols(safety, symbols):
    for s in symbols:
        safety.add_symbol(s)


class TestPower:
    def test_power_get(self, server_power):
        url, station, pv = server_power

        print(box(dir(pv), f'[test_power_get]', 'power view: '))
        print(fox({k: v.symbol.variable for k, v in pv.pwr.pwr_sws.items()}, f'[test_power_get] power view', 'power switches:\n'))
        assert station.pwr == pv.pwr
        resp = requests.get(url)
        power_symbols = resp.json()
        print(box(power_symbols, f'[test_power_get] {url}', f'{resp.status_code}: '))

    def test_power_add(self, server_power):
        url, _, _ = server_power
        resp = requests.put(f'{url}/ir_led_pwr_1', json={'value': 1})
        print(box(resp.json() if resp.ok else 'Nope!', f'test_power_add RESP json (resp.json())', f'{resp.status_code}: '))

