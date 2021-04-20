from mjk_utils.cmd import script_dir
from types import SimpleNamespace
import json

_default_settings_filepath = script_dir()+"/settings.local.json"
_default_template_filepath = script_dir()+"/settings.template.json"


def load(path=_default_settings_filepath):
    data = _fill_settings(path)
    ns = SimpleNamespace(**data)
    return ns


def _fill_settings(path):
    template_dict = _load(_default_template_filepath)
    data_dict = _load(path)
    output_dict = dict()
    for key in template_dict.keys():
        value = data_dict.get(key)
        if value is not None:
            output_dict[key] = data_dict[key]
    return output_dict


def _load(path):
    try:
        with open(path) as file:
            data = json.load(file)
    except json.JSONDecodeError:
        data = {}
    return data
