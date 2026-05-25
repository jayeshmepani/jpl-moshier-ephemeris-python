from jpl_moshier_ephemeris import (
    JME_BODY_MOON,
    JME_BODY_SUN,
    JME_CALC_SPEED,
    JME_CALENDAR_GREGORIAN,
    JME_HOUSE_PLACIDUS,
    JME_SIDEREAL_LAHIRI,
    JmeEph,
    c_double,
    c_int,
    create_string_buffer,
)


def test_version() -> None:
    jme = JmeEph()
    version = create_string_buffer(256)

    ret = jme.jme_version(version, 256)

    assert ret
    assert version.value.decode().count(".") >= 1


def test_julian_day_conversion() -> None:
    jme = JmeEph()
    jd = jme.jme_julian_day(2000, 1, 1, 12.0, JME_CALENDAR_GREGORIAN)

    assert jd == 2451545.0

    year = (c_int * 1)()
    month = (c_int * 1)()
    day = (c_int * 1)()
    hour = (c_double * 1)()
    jme.jme_reverse_julian_day(jd, JME_CALENDAR_GREGORIAN, year, month, day, hour)

    assert year[0] == 2000
    assert month[0] == 1
    assert day[0] == 1
    assert hour[0] == 12.0


def test_sun_position() -> None:
    jme = JmeEph()
    xx = (c_double * 6)()
    err = create_string_buffer(256)

    result = jme.jme_calc_ut(2451545.0, JME_BODY_SUN, JME_CALC_SPEED, xx, err)

    assert result >= 0
    assert 270 < xx[0] < 300
    assert 0.9 < xx[2] < 1.1


def test_moon_position() -> None:
    jme = JmeEph()
    xx = (c_double * 6)()
    err = create_string_buffer(256)

    result = jme.jme_calc_ut(2451545.0, JME_BODY_MOON, JME_CALC_SPEED, xx, err)

    assert result >= 0
    assert -6 < xx[1] < 6
    assert 10 < xx[3] < 16


def test_house_calculation() -> None:
    jme = JmeEph()
    cusps = (c_double * 13)()
    ascmc = (c_double * 10)()

    result = jme.jme_houses(2451545.0, 40.7128, -74.0060, JME_HOUSE_PLACIDUS, cusps, ascmc)

    assert result >= 0
    assert cusps[1] != 0.0


def test_ayanamsa() -> None:
    jme = JmeEph()

    jme.jme_set_sidereal_mode(JME_SIDEREAL_LAHIRI, 0.0, 0.0)
    ayanamsa = jme.jme_get_ayanamsa_ut(2451545.0)

    assert 23.0 < ayanamsa < 24.5


def test_delta_t() -> None:
    jme = JmeEph()
    deltat = jme.jme_delta_t(2451545.0)

    assert 60.0 < deltat < 70.0


def test_split_degrees() -> None:
    jme = JmeEph()
    ideg = (c_int * 1)()
    imin = (c_int * 1)()
    isec = (c_int * 1)()
    dsecfr = (c_double * 1)()
    isgn = (c_int * 1)()

    jme.jme_split_degree(123.456789, 0, ideg, imin, isec, dsecfr, isgn)

    assert ideg[0] == 123
    assert imin[0] == 27
    assert isec[0] >= 24


def test_body_name() -> None:
    jme = JmeEph()
    name = create_string_buffer(256)

    ret = jme.jme_copy_body_name(JME_BODY_SUN, name)

    assert ret
    assert name.value


def test_refraction() -> None:
    jme = JmeEph()
    refraction = jme.jme_refract(0.0, 1013.25, 15.0, 0)

    assert 0.4 < refraction < 0.6
