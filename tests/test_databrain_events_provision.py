import importlib.util
from pathlib import Path
import pytest


def load():
    path = Path(__file__).parents[1] / 'scripts/provision_databrain_events.py'
    spec = importlib.util.spec_from_file_location('provision_databrain_events', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_provisions_authenticated_loopback_route_without_replacing_telegram():
    m = load()
    result = m.with_route({'platforms': {'telegram': {'enabled': True}}}, 'x' * 64)
    assert result['platforms']['telegram'] == {'enabled': True}
    hook = result['platforms']['webhook']
    assert hook['extra']['host'] == '127.0.0.1'
    route = hook['extra']['routes']['databrain-execution']
    assert route['secret'] == 'x' * 64
    assert route['deliver'] == 'log'
    assert 'databrain_ack_event' in route['prompt']


def test_does_not_rebind_an_existing_nonloopback_listener():
    with pytest.raises(ValueError):
        load().with_route({'platforms': {'webhook': {'enabled': True, 'extra': {'host': '0.0.0.0'}}}}, 'x' * 64)
