import pytest
from jpl_moshier_ephemeris import JmeEph, signature_names
from jpl_moshier_ephemeris.bindings import _SIGNATURES


@pytest.mark.parametrize("name", sorted(signature_names()))
def test_all_204_c_functions_are_loaded(name: str) -> None:
    jme = JmeEph()
    fn = getattr(jme.lib, name)

    assert name in _SIGNATURES
    assert hasattr(jme, name)
    assert fn.argtypes == _SIGNATURES[name][1]
    assert fn.restype == _SIGNATURES[name][0]


def test_exactly_204_signatures_are_configured() -> None:
    assert len(list(signature_names())) == 204
