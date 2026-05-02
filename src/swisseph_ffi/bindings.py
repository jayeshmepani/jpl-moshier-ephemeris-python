"""Raw ctypes binding for the Swiss Ephemeris C API.

This module configures ctypes signatures only. It does not recalculate,
round, normalize, reshape arrays, hide return flags, or drop ``serr`` buffers.
Callers pass ctypes buffers/pointers exactly as the C API requires.
"""

from __future__ import annotations

from collections.abc import Iterable
from ctypes import CDLL, POINTER, byref, c_char, c_char_p, c_double, c_int, create_string_buffer
from pathlib import Path

from ._loader import find_library

_SIGNATURES = {
    "swe_heliacal_ut": (
        c_int,
        [
            c_double,
            POINTER(c_double),
            POINTER(c_double),
            POINTER(c_double),
            c_char_p,
            c_int,
            c_int,
            POINTER(c_double),
            c_char_p,
        ],
    ),
    "swe_heliacal_pheno_ut": (
        c_int,
        [
            c_double,
            POINTER(c_double),
            POINTER(c_double),
            POINTER(c_double),
            c_char_p,
            c_int,
            c_int,
            POINTER(c_double),
            c_char_p,
        ],
    ),
    "swe_vis_limit_mag": (
        c_int,
        [
            c_double,
            POINTER(c_double),
            POINTER(c_double),
            POINTER(c_double),
            c_char_p,
            c_int,
            POINTER(c_double),
            c_char_p,
        ],
    ),
    "swe_heliacal_angle": (
        c_int,
        [
            c_double,
            POINTER(c_double),
            POINTER(c_double),
            POINTER(c_double),
            c_int,
            c_double,
            c_double,
            c_double,
            c_double,
            c_double,
            POINTER(c_double),
            c_char_p,
        ],
    ),
    "swe_topo_arcus_visionis": (
        c_int,
        [
            c_double,
            POINTER(c_double),
            POINTER(c_double),
            POINTER(c_double),
            c_int,
            c_double,
            c_double,
            c_double,
            c_double,
            c_double,
            c_double,
            POINTER(c_double),
            c_char_p,
        ],
    ),
    "swe_set_astro_models": (None, [c_char_p, c_int]),
    "swe_get_astro_models": (None, [c_char_p, c_char_p, c_int]),
    "swe_version": (c_char_p, [c_char_p]),
    "swe_get_library_path": (c_char_p, [c_char_p]),
    "swe_calc": (c_int, [c_double, c_int, c_int, POINTER(c_double), c_char_p]),
    "swe_calc_ut": (c_int, [c_double, c_int, c_int, POINTER(c_double), c_char_p]),
    "swe_calc_pctr": (c_int, [c_double, c_int, c_int, c_int, POINTER(c_double), c_char_p]),
    "swe_solcross": (c_double, [c_double, c_double, c_int, c_char_p]),
    "swe_solcross_ut": (c_double, [c_double, c_double, c_int, c_char_p]),
    "swe_mooncross": (c_double, [c_double, c_double, c_int, c_char_p]),
    "swe_mooncross_ut": (c_double, [c_double, c_double, c_int, c_char_p]),
    "swe_mooncross_node": (
        c_double,
        [c_double, c_int, POINTER(c_double), POINTER(c_double), c_char_p],
    ),
    "swe_mooncross_node_ut": (
        c_double,
        [c_double, c_int, POINTER(c_double), POINTER(c_double), c_char_p],
    ),
    "swe_helio_cross": (
        c_int,
        [c_int, c_double, c_double, c_int, c_int, POINTER(c_double), c_char_p],
    ),
    "swe_helio_cross_ut": (
        c_int,
        [c_int, c_double, c_double, c_int, c_int, POINTER(c_double), c_char_p],
    ),
    "swe_fixstar": (c_int, [c_char_p, c_double, c_int, POINTER(c_double), c_char_p]),
    "swe_fixstar_ut": (c_int, [c_char_p, c_double, c_int, POINTER(c_double), c_char_p]),
    "swe_fixstar_mag": (c_int, [c_char_p, POINTER(c_double), c_char_p]),
    "swe_fixstar2": (c_int, [c_char_p, c_double, c_int, POINTER(c_double), c_char_p]),
    "swe_fixstar2_ut": (c_int, [c_char_p, c_double, c_int, POINTER(c_double), c_char_p]),
    "swe_fixstar2_mag": (c_int, [c_char_p, POINTER(c_double), c_char_p]),
    "swe_close": (None, []),
    "swe_set_ephe_path": (None, [c_char_p]),
    "swe_set_jpl_file": (None, [c_char_p]),
    "swe_get_planet_name": (c_char_p, [c_int, c_char_p]),
    "swe_set_topo": (None, [c_double, c_double, c_double]),
    "swe_set_sid_mode": (None, [c_int, c_double, c_double]),
    "swe_get_ayanamsa_ex": (c_int, [c_double, c_int, POINTER(c_double), c_char_p]),
    "swe_get_ayanamsa_ex_ut": (c_int, [c_double, c_int, POINTER(c_double), c_char_p]),
    "swe_get_ayanamsa": (c_double, [c_double]),
    "swe_get_ayanamsa_ut": (c_double, [c_double]),
    "swe_get_ayanamsa_name": (c_char_p, [c_int]),
    "swe_get_current_file_data": (
        c_char_p,
        [c_int, POINTER(c_double), POINTER(c_double), POINTER(c_int)],
    ),
    "swe_date_conversion": (c_int, [c_int, c_int, c_int, c_double, c_char, POINTER(c_double)]),
    "swe_julday": (c_double, [c_int, c_int, c_int, c_double, c_int]),
    "swe_revjul": (
        None,
        [c_double, c_int, POINTER(c_int), POINTER(c_int), POINTER(c_int), POINTER(c_double)],
    ),
    "swe_utc_to_jd": (
        c_int,
        [c_int, c_int, c_int, c_int, c_int, c_double, c_int, POINTER(c_double), c_char_p],
    ),
    "swe_jdet_to_utc": (
        None,
        [
            c_double,
            c_int,
            POINTER(c_int),
            POINTER(c_int),
            POINTER(c_int),
            POINTER(c_int),
            POINTER(c_int),
            POINTER(c_double),
        ],
    ),
    "swe_jdut1_to_utc": (
        None,
        [
            c_double,
            c_int,
            POINTER(c_int),
            POINTER(c_int),
            POINTER(c_int),
            POINTER(c_int),
            POINTER(c_int),
            POINTER(c_double),
        ],
    ),
    "swe_utc_time_zone": (
        None,
        [
            c_int,
            c_int,
            c_int,
            c_int,
            c_int,
            c_double,
            c_double,
            POINTER(c_int),
            POINTER(c_int),
            POINTER(c_int),
            POINTER(c_int),
            POINTER(c_int),
            POINTER(c_double),
        ],
    ),
    "swe_houses": (
        c_int,
        [c_double, c_double, c_double, c_int, POINTER(c_double), POINTER(c_double)],
    ),
    "swe_houses_ex": (
        c_int,
        [c_double, c_int, c_double, c_double, c_int, POINTER(c_double), POINTER(c_double)],
    ),
    "swe_houses_ex2": (
        c_int,
        [
            c_double,
            c_int,
            c_double,
            c_double,
            c_int,
            POINTER(c_double),
            POINTER(c_double),
            POINTER(c_double),
            POINTER(c_double),
            c_char_p,
        ],
    ),
    "swe_houses_armc": (
        c_int,
        [c_double, c_double, c_double, c_int, POINTER(c_double), POINTER(c_double)],
    ),
    "swe_houses_armc_ex2": (
        c_int,
        [
            c_double,
            c_double,
            c_double,
            c_int,
            POINTER(c_double),
            POINTER(c_double),
            POINTER(c_double),
            POINTER(c_double),
            c_char_p,
        ],
    ),
    "swe_house_pos": (c_double, [c_double, c_double, c_double, c_int, POINTER(c_double), c_char_p]),
    "swe_house_name": (c_char_p, [c_int]),
    "swe_gauquelin_sector": (
        c_int,
        [
            c_double,
            c_int,
            c_char_p,
            c_int,
            c_int,
            POINTER(c_double),
            c_double,
            c_double,
            POINTER(c_double),
            c_char_p,
        ],
    ),
    "swe_sol_eclipse_where": (
        c_int,
        [c_double, c_int, POINTER(c_double), POINTER(c_double), c_char_p],
    ),
    "swe_lun_occult_where": (
        c_int,
        [c_double, c_int, c_char_p, c_int, POINTER(c_double), POINTER(c_double), c_char_p],
    ),
    "swe_sol_eclipse_how": (
        c_int,
        [c_double, c_int, POINTER(c_double), POINTER(c_double), c_char_p],
    ),
    "swe_sol_eclipse_when_loc": (
        c_int,
        [c_double, c_int, POINTER(c_double), POINTER(c_double), POINTER(c_double), c_int, c_char_p],
    ),
    "swe_lun_occult_when_loc": (
        c_int,
        [
            c_double,
            c_int,
            c_char_p,
            c_int,
            POINTER(c_double),
            POINTER(c_double),
            POINTER(c_double),
            c_int,
            c_char_p,
        ],
    ),
    "swe_sol_eclipse_when_glob": (
        c_int,
        [c_double, c_int, c_int, POINTER(c_double), c_int, c_char_p],
    ),
    "swe_lun_occult_when_glob": (
        c_int,
        [c_double, c_int, c_char_p, c_int, c_int, POINTER(c_double), c_int, c_char_p],
    ),
    "swe_lun_eclipse_how": (
        c_int,
        [c_double, c_int, POINTER(c_double), POINTER(c_double), c_char_p],
    ),
    "swe_lun_eclipse_when": (c_int, [c_double, c_int, c_int, POINTER(c_double), c_int, c_char_p]),
    "swe_lun_eclipse_when_loc": (
        c_int,
        [c_double, c_int, POINTER(c_double), POINTER(c_double), POINTER(c_double), c_int, c_char_p],
    ),
    "swe_pheno": (c_int, [c_double, c_int, c_int, POINTER(c_double), c_char_p]),
    "swe_pheno_ut": (c_int, [c_double, c_int, c_int, POINTER(c_double), c_char_p]),
    "swe_refrac": (c_double, [c_double, c_double, c_double, c_int]),
    "swe_refrac_extended": (
        c_double,
        [c_double, c_double, c_double, c_double, c_double, c_int, POINTER(c_double)],
    ),
    "swe_set_lapse_rate": (None, [c_double]),
    "swe_azalt": (
        None,
        [
            c_double,
            c_int,
            POINTER(c_double),
            c_double,
            c_double,
            POINTER(c_double),
            POINTER(c_double),
        ],
    ),
    "swe_azalt_rev": (
        None,
        [c_double, c_int, POINTER(c_double), POINTER(c_double), POINTER(c_double)],
    ),
    "swe_rise_trans_true_hor": (
        c_int,
        [
            c_double,
            c_int,
            c_char_p,
            c_int,
            c_int,
            POINTER(c_double),
            c_double,
            c_double,
            c_double,
            POINTER(c_double),
            c_char_p,
        ],
    ),
    "swe_rise_trans": (
        c_int,
        [
            c_double,
            c_int,
            c_char_p,
            c_int,
            c_int,
            POINTER(c_double),
            c_double,
            c_double,
            POINTER(c_double),
            c_char_p,
        ],
    ),
    "swe_nod_aps": (
        c_int,
        [
            c_double,
            c_int,
            c_int,
            c_int,
            POINTER(c_double),
            POINTER(c_double),
            POINTER(c_double),
            POINTER(c_double),
            c_char_p,
        ],
    ),
    "swe_nod_aps_ut": (
        c_int,
        [
            c_double,
            c_int,
            c_int,
            c_int,
            POINTER(c_double),
            POINTER(c_double),
            POINTER(c_double),
            POINTER(c_double),
            c_char_p,
        ],
    ),
    "swe_get_orbital_elements": (c_int, [c_double, c_int, c_int, POINTER(c_double), c_char_p]),
    "swe_orbit_max_min_true_distance": (
        c_int,
        [c_double, c_int, c_int, POINTER(c_double), POINTER(c_double), POINTER(c_double), c_char_p],
    ),
    "swe_deltat": (c_double, [c_double]),
    "swe_deltat_ex": (c_double, [c_double, c_int, c_char_p]),
    "swe_time_equ": (c_int, [c_double, POINTER(c_double), c_char_p]),
    "swe_lmt_to_lat": (c_int, [c_double, c_double, POINTER(c_double), c_char_p]),
    "swe_lat_to_lmt": (c_int, [c_double, c_double, POINTER(c_double), c_char_p]),
    "swe_sidtime0": (c_double, [c_double, c_double, c_double]),
    "swe_sidtime": (c_double, [c_double]),
    "swe_set_interpolate_nut": (None, [c_int]),
    "swe_cotrans": (None, [POINTER(c_double), POINTER(c_double), c_double]),
    "swe_cotrans_sp": (None, [POINTER(c_double), POINTER(c_double), c_double]),
    "swe_get_tid_acc": (c_double, []),
    "swe_set_tid_acc": (None, [c_double]),
    "swe_set_delta_t_userdef": (None, [c_double]),
    "swe_degnorm": (c_double, [c_double]),
    "swe_radnorm": (c_double, [c_double]),
    "swe_rad_midp": (c_double, [c_double, c_double]),
    "swe_deg_midp": (c_double, [c_double, c_double]),
    "swe_split_deg": (
        None,
        [
            c_double,
            c_int,
            POINTER(c_int),
            POINTER(c_int),
            POINTER(c_int),
            POINTER(c_double),
            POINTER(c_int),
        ],
    ),
    "swe_csnorm": (c_int, [c_int]),
    "swe_difcsn": (c_int, [c_int, c_int]),
    "swe_difdegn": (c_double, [c_double, c_double]),
    "swe_difcs2n": (c_int, [c_int, c_int]),
    "swe_difdeg2n": (c_double, [c_double, c_double]),
    "swe_difrad2n": (c_double, [c_double, c_double]),
    "swe_csroundsec": (c_int, [c_int]),
    "swe_d2l": (c_int, [c_double]),
    "swe_day_of_week": (c_int, [c_double]),
    "swe_cs2timestr": (c_char_p, [c_int, c_int, c_int, c_char_p]),
    "swe_cs2lonlatstr": (c_char_p, [c_int, c_char, c_char, c_char_p]),
    "swe_cs2degstr": (c_char_p, [c_int, c_char_p]),
}


class SwissEph:
    """Direct runtime-FFI loader for the native Swiss Ephemeris library."""

    def __init__(self, library_path: str | Path | None = None) -> None:
        self.library_path = Path(library_path) if library_path is not None else find_library()
        self._lib = CDLL(str(self.library_path))
        self._configure_signatures()

    @property
    def lib(self) -> CDLL:
        """Return the underlying ctypes CDLL handle."""
        return self._lib

    def _configure_signatures(self) -> None:
        for name, (restype, argtypes) in _SIGNATURES.items():
            fn = getattr(self._lib, name)
            fn.restype = restype
            fn.argtypes = argtypes

    def __getattr__(self, name: str):
        if name in _SIGNATURES:
            return getattr(self._lib, name)
        raise AttributeError(name)


def signature_names() -> Iterable[str]:
    """Return all configured Swiss Ephemeris C function names."""
    return _SIGNATURES.keys()


__all__ = [
    "SwissEph",
    "signature_names",
    "byref",
    "create_string_buffer",
    "c_char",
    "c_char_p",
    "c_double",
    "c_int",
    "POINTER",
]
