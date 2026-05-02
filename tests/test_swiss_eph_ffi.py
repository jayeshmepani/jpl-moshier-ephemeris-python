from swisseph_ffi import (
    SE_GREG_CAL,
    SE_HOUSES_PLACIDUS,
    SE_MOON,
    SE_SIDM_LAHIRI,
    SE_SUN,
    SEFLG_SPEED,
    SwissEph,
    c_double,
    c_int,
    create_string_buffer,
)


def test_version() -> None:
    swe = SwissEph()
    version = create_string_buffer(256)

    ret = swe.swe_version(version)

    assert ret
    assert version.value.decode().count(".") >= 1


def test_julian_day_conversion() -> None:
    swe = SwissEph()
    jd = swe.swe_julday(2000, 1, 1, 12.0, SE_GREG_CAL)

    assert jd == 2451545.0

    year = (c_int * 1)()
    month = (c_int * 1)()
    day = (c_int * 1)()
    hour = (c_double * 1)()
    swe.swe_revjul(jd, SE_GREG_CAL, year, month, day, hour)

    assert year[0] == 2000
    assert month[0] == 1
    assert day[0] == 1
    assert hour[0] == 12.0


def test_sun_position() -> None:
    swe = SwissEph()
    xx = (c_double * 6)()
    serr = create_string_buffer(256)

    result = swe.swe_calc_ut(2451545.0, SE_SUN, SEFLG_SPEED, xx, serr)

    assert result >= 0
    assert 270 < xx[0] < 300
    assert 0.9 < xx[2] < 1.1


def test_moon_position() -> None:
    swe = SwissEph()
    xx = (c_double * 6)()
    serr = create_string_buffer(256)

    result = swe.swe_calc_ut(2451545.0, SE_MOON, SEFLG_SPEED, xx, serr)

    assert result >= 0
    assert -6 < xx[1] < 6
    assert 10 < xx[3] < 16


def test_house_calculation() -> None:
    swe = SwissEph()
    cusps = (c_double * 13)()
    ascmc = (c_double * 10)()

    result = swe.swe_houses(2451545.0, 40.7128, -74.0060, ord(SE_HOUSES_PLACIDUS), cusps, ascmc)

    assert result >= 0


def test_ayanamsa() -> None:
    swe = SwissEph()

    swe.swe_set_sid_mode(SE_SIDM_LAHIRI, 0.0, 0.0)
    ayanamsa = swe.swe_get_ayanamsa_ut(2451545.0)

    assert 23.0 < ayanamsa < 24.5


def test_delta_t() -> None:
    swe = SwissEph()
    deltat = swe.swe_deltat(2451545.0)

    assert 0.0007 < deltat < 0.0008


def test_split_degrees() -> None:
    swe = SwissEph()
    ideg = (c_int * 1)()
    imin = (c_int * 1)()
    isec = (c_int * 1)()
    dsecfr = (c_double * 1)()
    isgn = (c_int * 1)()

    swe.swe_split_deg(123.456789, 0, ideg, imin, isec, dsecfr, isgn)

    assert ideg[0] == 123
    assert imin[0] == 27
    assert isec[0] >= 24


def test_planet_name() -> None:
    swe = SwissEph()
    name = create_string_buffer(256)

    ret = swe.swe_get_planet_name(SE_SUN, name)

    assert ret
    assert name.value


def test_refraction() -> None:
    swe = SwissEph()
    refraction = swe.swe_refrac(0.0, 1013.25, 15.0, 0)

    assert 0.4 < refraction < 0.6
