"""Tests for the C engine API added in jpl-ephemeris PR #3.

Expected values were produced by the C library itself (printf %.17g) at
jpl-ephemeris c15031e; the wrapper must pass them through unchanged.
Arithmetic-only results are compared exactly; results that go through
libm transcendental functions allow 1e-14 relative (platform libm).
"""

from __future__ import annotations

import math
from ctypes import byref
from pathlib import Path

import pytest
from jpl_moshier_ephemeris import (
    JME_AYANAMSA_MEAN,
    JME_AYANAMSA_TRUE,
    JME_BODY_MARS,
    JME_ENGINE_ID_MOSHIER,
    JME_JPL_CENTER_STRICT,
    JME_MODEL_DELTAT_ESPENAK_MEEUS_2006,
    JME_MODEL_DELTAT_MS2004_TABLE1_LINEAR,
    JME_MODEL_DELTAT_STEPHENSON_ETC_2021,
    JME_MODEL_PREC_LASKAR_1986,
    JME_SIDEREAL_LAHIRI,
    JME_TIME_SCALE_TAI,
    JME_TIME_SCALE_TDB,
    JME_TIME_SCALE_TT,
    JME_TIME_SCALE_UTC,
    JME_TIME_TIDAL_AUTOMATIC,
    JME_TIME_TIDAL_DE441,
    JmeEph,
    c_double,
    c_int,
    create_string_buffer,
)

EOP = Path(__file__).parent / "fixtures" / "eop_finals2000A_excerpt.txt"


def close(a: float, b: float) -> bool:
    return math.isclose(a, b, rel_tol=1e-14, abs_tol=0.0)


@pytest.fixture()
def jme() -> JmeEph:
    j = JmeEph()
    j.jme_set_astro_models(b"DEFAULT", 0)
    j.jme_set_tid_acc(JME_TIME_TIDAL_AUTOMATIC)
    return j


def test_time_scale_convert_and_name(jme: JmeEph) -> None:
    o1, o2, err = c_double(), c_double(), create_string_buffer(256)
    rc = jme.jme_time_scale_convert(
        2451545.0, 0.0, JME_TIME_SCALE_TT, JME_TIME_SCALE_TAI, byref(o1), byref(o2), err
    )
    assert rc == 0
    assert (o1.value, o2.value) == (2451545.0, -0.00037249999999999995)
    jme.jme_time_scale_convert(
        2457754.5, 0.25, JME_TIME_SCALE_UTC, JME_TIME_SCALE_TT, byref(o1), byref(o2), err
    )
    assert (o1.value, o2.value) == (2457754.5, 0.25080074074074071)
    assert jme.jme_time_scale_name(JME_TIME_SCALE_TDB) == b"TDB"


def test_table_info(jme: JmeEph) -> None:
    a, b, c, err = c_double(), c_double(), c_double(), create_string_buffer(256)
    assert jme.jme_leap_second_table_info(byref(a), byref(b), err) == 0
    assert (a.value, b.value) == (2461587.5, 37.0)
    assert jme.jme_delta_t_iers_table_info(byref(a), byref(b), byref(c), err) == 0
    assert (a.value, b.value, c.value) == (2441684.5, 2461321.5, 2461682.5)


def test_ayanamsa_ex2_and_sidereal_time_ex(jme: JmeEph) -> None:
    ay, rate, err = c_double(), c_double(), create_string_buffer(256)
    jme.jme_set_sidereal_mode(JME_SIDEREAL_LAHIRI, 0.0, 0.0)
    rc = jme.jme_get_ayanamsa_ex2(
        2451545.0, JME_SIDEREAL_LAHIRI, JME_AYANAMSA_TRUE, byref(ay), byref(rate), err
    )
    assert rc == 0
    assert close(ay.value, 23.853224722663143)
    assert close(rate.value, 3.8246992136024994e-05)
    jme.jme_get_ayanamsa_ex2_ut(
        2451545.0, JME_SIDEREAL_LAHIRI, JME_AYANAMSA_MEAN, byref(ay), byref(rate), err
    )
    assert close(ay.value, 23.857092357910052)
    hours = c_double()
    assert jme.jme_sidereal_time_ex(2451545.0, 1, byref(hours), err) == 0
    assert close(hours.value, 18.69713803335517)


def test_houses_gauquelin(jme: JmeEph) -> None:
    cusps, ascmc, err = (c_double * 37)(), (c_double * 10)(), create_string_buffer(256)
    assert jme.jme_houses_gauquelin(2451545.0, 0, 28.6, 77.2, cusps, ascmc, err) == 0
    assert close(cusps[1], 100.17642650805641)
    assert close(cusps[19], 280.17642650805641)
    assert close(cusps[36], 107.65087247267206)
    assert close(ascmc[0], 100.17642650805641)
    assert jme.jme_houses_gauquelin_armc(100.0, 28.6, 23.44, cusps, ascmc, err) == 0
    assert close(cusps[10], 99.18946523149512)
    assert close(cusps[36], 197.96278849881179)


def test_engine_resolution_and_center_policy(jme: JmeEph) -> None:
    eid, sub, err = c_int(-1), c_int(-1), create_string_buffer(256)
    assert jme.jme_calc_resolve_engine(2451545.0, JME_BODY_MARS, byref(eid), byref(sub), err) == 0
    assert (eid.value, sub.value) == (JME_ENGINE_ID_MOSHIER, 0)
    assert jme.jme_set_jpl_center_policy(7, err) == -1
    assert err.value
    assert jme.jme_get_jpl_center_policy() == JME_JPL_CENTER_STRICT


def test_checked_setters_and_laskar(jme: JmeEph) -> None:
    err = create_string_buffer(256)
    assert jme.jme_set_astro_models_checked(b"NOPE_TOKEN", err) == -1
    assert jme.jme_set_astro_models_checked(b"PREC=LASKAR1986", err) == 0
    m = (c_double * 9)()
    rc = jme.jme_get_precession_matrix(
        2451545.0, 2451545.0 + 36525.0, JME_MODEL_PREC_LASKAR_1986, m
    )
    assert rc == 0
    assert close(m[0], 0.99970264828061839)
    assert close(m[1], -0.022366275629188623)
    assert jme.jme_set_topo_checked(0.0, 95.0, 0.0, err) == -1
    assert jme.jme_set_sidereal_mode_checked(99999, 0.0, 0.0, err) == -1


def test_eop_and_polar_motion(jme: JmeEph) -> None:
    a, b, err = c_double(), c_double(), create_string_buffer(256)
    jme.jme_eop_clear()
    assert jme.jme_eop_coverage(byref(a), byref(b), err) == -1
    assert jme.jme_eop_load_file(str(EOP).encode(), err) == 0
    assert jme.jme_eop_coverage(byref(a), byref(b), err) == 0
    assert (a.value, b.value) == (58845.0, 60314.0)
    pred = c_int(-1)
    assert jme.jme_eop_polar_motion(58849.25, byref(a), byref(b), byref(pred), err) == 0
    assert (a.value, b.value, pred.value) == (0.076103695312499997, 0.28242803124999993, 0)
    assert jme.jme_eop_polar_motion(59000.0, byref(a), byref(b), byref(pred), err) == -1
    jme.jme_set_polar_motion(1)
    assert jme.jme_get_polar_motion() == 1
    jme.jme_set_polar_motion(0)
    assert jme.jme_get_polar_motion() == 0
    jme.jme_eop_clear()
    assert jme.jme_eop_coverage(byref(a), byref(b), err) == -1


def test_delta_t_models_and_de441_error(jme: JmeEph) -> None:
    err = create_string_buffer(256)
    jme.jme_set_tid_acc(JME_TIME_TIDAL_DE441)
    dt = jme.jme_delta_t_ex(2000000.0, JME_MODEL_DELTAT_ESPENAK_MEEUS_2006, err)
    assert math.isnan(dt)
    assert b"DE441" in err.value
    jme.jme_set_tid_acc(JME_TIME_TIDAL_AUTOMATIC)
    ms04 = jme.jme_delta_t_ex(2000000.0, JME_MODEL_DELTAT_MS2004_TABLE1_LINEAR, err)
    smh21 = jme.jme_delta_t_ex(2000000.0, JME_MODEL_DELTAT_STEPHENSON_ETC_2021, err)
    assert close(ms04, 3268.5267123287672)
    assert close(smh21, 3229.007157575752)
