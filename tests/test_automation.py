import requests

from tests.utils import *

def add_symbols(safety, symbols):
    for s in symbols:
        safety.add_symbol(s)

class TestAutomation:
    def test_automation_get(self, server_automation):
        url, psa, av, _ = server_automation
        # print('[test_automation_get] PSA')
        # pp(psa.namespace)
        print(fox(av._variables, '[test_automation_get] AV variables'))
        print(fox(av.commands.keys(), '[test_automation_get] AV commands'))
        print(fox(psa.programs.keys(), '[test_automation_get] PSA programs'))
        print(f'[test_automation_get] calling {url}')
        resp = requests.get(url)
        print(fox(resp.json(), '[test_automation_get] resp.json()'))
        avv = av._variables_val()
        avv['error'] = list(avv['error'])
        assert avv == resp.json()
        print(fox(avv, '[test_automation_get] AV variables\' values'))
        for v in av._variables:
            print(f'[test_automation_get] calling {url}/{v}')
            resp = requests.get(f'{url}/{v}')
            print(f'[test_automation_get] got {resp}')
            print(box(resp.json(), f'[test_automation_get] /automation/{v}'))
            assert resp.ok
            assert resp.json()['value'] == avv[v]

    def test_automation_commands(self, server_automation):
        url, _, av, _ = server_automation
        commands = ['start', 'stop', 'pause', 'resume', 'state', 'show', 'adjustment_done']
        for command in (k for k in av.commands.keys() if not k in ['disable_patient_validation', 'emergency']):
            if command not in ['adjust', 'switch_program']:
                resp = requests.get(url, json={'command': command})
                assert resp.ok
                print(fox(resp.json() if resp.ok else resp.status_code, f'[test_automation_commands] /automation/{command}', 'resp.json:'))
                print(fox(av._variables_val() if resp.ok else resp.status_code, f'[test_automation_commands] /automation/{command}'))

    def test_automation_reset(self, server_automation):
        url, _, av, sim = server_automation
        print(fox(sim.name, f'[test_automation_reset] name'))
        print(fox(sim.env, f'[test_automation_reset] environment'))
        print(fox(list(map(lambda sym: (sym.module, sym.variable, sym.reference), sim.symbol_table.symbols)), f'[test_automation_reset] symbol table'))
        '''
        PUT http://127.0.0.1:5003/safety/safety_mtr_on, {value: true}
        PUT http://127.0.0.1:5003/automation, {command: "start"}
        '''

        resp_show = requests.get(url, json={'command': 'show'})
        rsh_json = resp_show.json()
        resp_state = requests.get(url, json={'command': 'state'})
        rst_json = resp_state.json()

        # resp = requests.get(url, json={'command': 'start'})
        # val = av._variable_val('running')
        # print(fox(val if resp.ok else resp.status_code, f'[test_automation_start_stop] /automation/start'))
        # assert resp.ok
        # assert val == 'running'
        # resp = requests.get(url, json={'command': 'stop'})
        # val = av._variable_val('running')
        # print(fox(val if resp.ok else resp.status_code, f'[test_automation_start_stop] /automation/start'))
        # assert resp.ok
        # assert val == 'stopped'

    def test_automation_show_state(self, server_automation):
        url, _, av, _ = server_automation
        resp_show = requests.get(url, json={'command': 'show'})
        assert resp_show.ok
        rsh_json = resp_show.json()
        print(fox(rsh_json, f'[test_automation_show_state] /automation/start'))
        resp_state = requests.get(url, json={'command': 'state'})
        assert resp_state.ok
        rst_json = resp_state.json()
        print(fox(rst_json, f'[test_automation_show_state] /automation/start'))
        assert rsh_json['state'] == rst_json['recursive'] and rsh_json['bstate'] == rst_json['state'] 

    def test_automation_start_stop(self, server_automation):
        url, _, av, _ = server_automation
        resp = requests.get(url, json={'command': 'start'})
        val = av._variable_val('running')
        print(fox(val if resp.ok else resp.status_code, f'[test_automation_start_stop] /automation/start'))
        assert resp.ok
        assert val == 'running'
        resp = requests.get(url, json={'command': 'stop'})
        val = av._variable_val('running')
        print(fox(val if resp.ok else resp.status_code, f'[test_automation_start_stop] /automation/start'))
        assert resp.ok
        assert val == 'stopped'

    def test_automation_start_pause_resume_stop(self, server_automation):
        url, _, av, _ = server_automation
        commands = (('start', 'running'), ('pause', 'paused'), ('resume', 'running'), ('stop', 'stopped'), )
        for command in commands:
            resp = requests.get(url, json={'command': command[0]})
            val = av._variable_val('running')
            print(fox(val if resp.ok else resp.status_code, f'[test_automation_start_pause_resume_stop] /automation/{command}'))
            assert resp.ok
            assert val == command[1]

    def test_automation_adjustment_done(self, server_automation):
        url, psa, _, _ = server_automation
        print(box(psa.namespace.adjustment_done, f'[test_automation_adjustment_done] /automation/adjustment_done'))
        assert not psa.namespace.adjustment_done
        requests.get(url, json={'command': 'adjustment_done'})
        print(box(psa.namespace.adjustment_done, f'[test_automation_adjustment_done] /automation/adjustment_done'))
        assert psa.namespace.adjustment_done

    def test_automation_switch_program(self, server_automation):
        url, _, av, _ = server_automation
        for program in (p for p in av._variable_val('programs')):
            resp = requests.get(url, json={'command': 'switch_program', 'data': program})
            print(fox(av._variables_val() if resp.ok else resp.status_code, f'[test_automation_switch_program] {program}', f'{resp.json()} ({resp.headers["Content-Type"]})\n'))

    def test_automation_adjust(self, server_automation):
        url, _, av, _ = server_automation
        for action in (p for p in av.automation_adjust.actions.keys()):
            resp = requests.get(url, json={'command': 'adjust', 'data': action})
            print(fox(av._variables_val() if resp.ok else resp.status_code, f'[test_automation_adjust] {action}', f'{resp.text} ({resp.headers["Content-Type"]})\n'))
        print(fox([(x, catch(getattr(resp, x))) if not x.startswith('_') and callable(getattr(resp, x)) else (x, getattr(resp, x)) for x in dir(resp)], 'adjust response features'))

