import pytest
from swisseph_ffi import SwissEph, signature_names
from swisseph_ffi.bindings import _SIGNATURES


@pytest.mark.parametrize("name", sorted(signature_names()))
def test_all_106_c_functions_are_loaded(name: str) -> None:
    swe = SwissEph()
    fn = getattr(swe.lib, name)

    assert name in _SIGNATURES
    assert hasattr(swe, name)
    assert fn.argtypes == _SIGNATURES[name][1]
    assert fn.restype == _SIGNATURES[name][0]


def test_exactly_106_signatures_are_configured() -> None:
    assert len(list(signature_names())) == 106
