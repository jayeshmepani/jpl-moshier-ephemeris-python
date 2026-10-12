import pytest
from jpl_moshier_ephemeris import JmeEph, signature_names
from jpl_moshier_ephemeris.bindings import _OPTIONAL_SIGNATURES, _SIGNATURES, optional_signature_names


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


def test_optional_core_api_signatures_are_declared_and_configured_when_available() -> None:
    optional_names = set(optional_signature_names())
    assert optional_names == set(_OPTIONAL_SIGNATURES)
    assert len(optional_names) == 15

    jme = JmeEph()
    for name in optional_names:
        expected_restype, expected_argtypes = _OPTIONAL_SIGNATURES[name]
        try:
            fn = getattr(jme.lib, name)
        except AttributeError:
            # Older released native bundles predate these additive APIs.
            continue

        assert hasattr(jme, name)
        assert fn.argtypes == expected_argtypes
        assert fn.restype == expected_restype
