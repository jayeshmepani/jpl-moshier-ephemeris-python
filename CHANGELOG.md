# Changelog

## 2.0.0 — unreleased

Align Python constants with JME 2.0.0. Extended-body identifiers now use JME's reserved negative range, so applications that stored their previous numeric values must migrate to the named constants. Function signatures and the 225-function, 478-constant API surface are unchanged.

The bundled runtimes are rebuilt from native commit `ab153fd7a58705cd1732bb226cb5fb2655f5c290`. Each runtime notice records the same commit, and the Linux x64 runtime reports `2.0.0` through `jme_version()`.

## 1.3.1

Package 1.3.1 replaces 1.3.0. `JME_VERSION` stays `1.3.0`. The public surface is unchanged: 225 functions and 478 public constants, plus the two header include guards `JME_JME_H` and `JME_EXTENDED_H`.

The 1.3.0 package still contained the previous libraries, native commit `e371446`, whose `jme_version()` returns `0.1.0`. This package ships the rebuilt libraries, native commit `fd0fcf5`. `jme_version()` returns `1.3.0`.

## 1.3.0

Version alignment with jpl-ephemeris 1.3.0. `JME_VERSION` is `1.3.0`. The public surface is unchanged: 225 functions and 478 public constants, plus the two header include guards `JME_JME_H` and `JME_EXTENDED_H`.

The native library is the ISO C17 build. Position-only paths inside the library skip a discarded velocity. Public `jme_calc_ut` still returns six values, including the rates. The published reduction is unchanged.

The 1.3.0 package upload did not contain the rebuilt runtimes. 1.3.1 does.

## 1.1.0

Bindings for jpl-ephemeris 1.1.0. Runtimes are rebuilt from 1.1.0, with notices. Desktop CALCEPH is now 5.0.1.

### Native API added in jpl-ephemeris 1.1.0

The wrapper maps these 21 functions one-to-one onto the native entry points (same argument order, pointer outputs and error buffer; no rounding, defaults or reshaping). Signatures are verified against the C headers.


#### Time scales

- `int jme_time_scale_convert(double jd1, double jd2, int from_scale, int to_scale, double *out1, double *out2, char *error);`<br>Converts a two-part Julian date between UTC, UT1, TAI, TT, TDB, TCG and TCB (JME_TIME_SCALE_*), preserving the split where possible. UTC follows the ERFA/SOFA quasi-JD convention on leap-second days and is defined from 1960-01-01 until the leap-second table expiry. UT1 uses the context Delta-T model. Returns: JME_OK or JME_ERR; out1/out2 receive the converted two-part date.
- `const char *jme_time_scale_name(int scale);`<br>Returns the name of a JME_TIME_SCALE_* value (for example "TDB"). Returns: Static string owned by the library; do not free.
- `int jme_leap_second_table_info(double *jd_utc_valid_until, double *last_tai_minus_utc, char *error);`<br>Reports the embedded IERS Bulletin C leap-second table: the first UTC Julian date it no longer covers and the latest TAI-UTC in seconds. Either pointer may be NULL, but not both. Returns: JME_OK or JME_ERR.
- `int jme_delta_t_iers_table_info(double *jd_first, double *jd_last_observed, double *jd_last, char *error);`<br>Reports the embedded IERS finals2000A Delta-T table used by JME_TIME_DELTAT_AUTOMATIC: first day, last observed day and last predicted day (UTC Julian dates). Returns: JME_OK or JME_ERR.
- `int jme_sidereal_time_ex(double jd_ut, int apparent, double *hours, char *error);`<br>Greenwich sidereal time in hours for UT1 jd_ut; apparent = 0 gives mean sidereal time, apparent != 0 adds the equation of the equinoxes of the context nutation model. Returns: JME_OK or JME_ERR; hours receives the sidereal time.

#### Sidereal

- `int jme_get_ayanamsa_ex2(double jd_et, int model, int flags, double *ayan, double *rate, char *error);`<br>Ayanamsa (degrees) with explicit JME_AYANAMSA_MEAN or JME_AYANAMSA_TRUE (mean plus nutation in longitude of the context nutation model). rate (optional, may be NULL) receives the rate of the mean ayanamsa in degrees/day. Returns: JME_OK or JME_ERR.
- `int jme_get_ayanamsa_ex2_ut(double jd_ut, int model, int flags, double *ayan, double *rate, char *error);`<br>As jme_get_ayanamsa_ex2 for a UT1 Julian date. Returns: JME_OK or JME_ERR.

#### Houses

- `int jme_houses_gauquelin(double jd_ut, int flags, double geo_lat, double geo_lon, double *cusps, double *ascmc, char *error);`<br>The 36 Gauquelin sector cusps. cusps must hold 37 doubles: [1] = Ascendant, [10] = MC, [19] = Descendant, [28] = IC, numbered in the direction of diurnal motion; cusps[0] = 0. ascmc (optional) holds 10 doubles as in jme_houses_ex. flags: JME_CALC_NO_NUTATION, JME_CALC_SIDEREAL. Returns: JME_OK or JME_ERR (JME_ERR where a semi-arc is undefined, at polar latitudes).
- `int jme_houses_gauquelin_armc(double armc, double geo_lat, double eps, double *cusps, double *ascmc, char *error);`<br>As jme_houses_gauquelin from ARMC and obliquity (degrees); cusps holds 37 doubles. Returns: JME_OK or JME_ERR.

#### Engine policy

- `int jme_calc_resolve_engine(double jd_et, int body, int *engine_id, int *jpl_center_substituted, char *error);`<br>Reports which engine jme_calc uses for body at jd_et (TT) under the current settings (JME_ENGINE_ID_*), so ENGINE=AUTO never substitutes a model silently. jpl_center_substituted (optional) is 1 when a JPL planet centre was replaced by its system barycentre under JME_JPL_CENTER_BARYCENTER. Returns: JME_OK or JME_ERR.
- `int jme_set_jpl_center_policy(int policy, char *error);`<br>Sets the JPL planet-centre policy: JME_JPL_CENTER_STRICT (default; a missing planet centre is an error, or makes ENGINE=AUTO use the analytical engine) or JME_JPL_CENTER_BARYCENTER (opt-in system barycentre). Returns: JME_OK or JME_ERR for an unknown policy.
- `int jme_get_jpl_center_policy(void);`<br>Returns the current JME_JPL_CENTER_* policy. Returns: JME_JPL_CENTER_STRICT or JME_JPL_CENTER_BARYCENTER.

#### Validating setters

- `int jme_set_astro_models_checked(const char *models, char *error);`<br>As jme_set_astro_models, but unknown or over-long tokens are errors and leave the configuration unchanged. Accepts PREC=LASKAR1986 among the model tokens. Returns: JME_OK or JME_ERR.
- `int jme_set_topo_checked(double lon, double lat, double altitude, char *error);`<br>As jme_set_topo, but non-finite values or |lat| > 90 are errors; longitude is normalised to [-180, 180). Returns: JME_OK or JME_ERR.
- `int jme_set_sidereal_mode_checked(int sidereal_mode, double t0, double ayan_t0, char *error);`<br>As jme_set_sidereal_mode, but unknown modes or non-finite t0/ayan_t0 are errors. Returns: JME_OK or JME_ERR.

#### Earth orientation (polar motion)

- `int jme_eop_load_file(const char *path, char *error);`<br>Loads an IERS finals2000A or EOP C04 file (format detected) and replaces any loaded series. The series is process-global: load it before using it from several threads. Returns: JME_OK or JME_ERR.
- `void jme_eop_clear(void);`<br>Discards the loaded EOP series. Returns: None.
- `int jme_eop_coverage(double *mjd_first, double *mjd_last, char *error);`<br>First and last MJD of the loaded EOP series. Returns: JME_OK, or JME_ERR when no series is loaded.
- `int jme_eop_polar_motion(double mjd, double *xp_arcsec, double *yp_arcsec, int *predicted, char *error);`<br>Pole coordinates xp, yp (arcsec) at an MJD by 4-point Lagrange interpolation (IERS scheme); predicted != 0 when a prediction row contributed. No extrapolation: dates outside the series or across gaps are errors. Returns: JME_OK or JME_ERR.
- `void jme_set_polar_motion(int enabled);`<br>enabled != 0 applies the polar-motion matrix W = eraPom00(xp, yp, s') to topocentric observer positions, horizontal coordinates and eclipse geographic mappings; those computations then fail with an error when no EOP data cover the date. Default 0 (no polar motion). Returns: None.
- `int jme_get_polar_motion(void);`<br>Returns 1 when polar motion is enabled, else 0. Returns: 0 or 1.

#### New constants

| Constant | Value | Meaning |
|---|---|---|
| `JME_TIME_SCALE_UTC` | `0` | Time scale for jme_time_scale_convert (ABI value). |
| `JME_TIME_SCALE_UT1` | `1` | Time scale for jme_time_scale_convert (realised with the context Delta-T model). |
| `JME_TIME_SCALE_TAI` | `2` | Time scale for jme_time_scale_convert. |
| `JME_TIME_SCALE_TT` | `3` | Time scale for jme_time_scale_convert. |
| `JME_TIME_SCALE_TDB` | `4` | Time scale for jme_time_scale_convert. |
| `JME_TIME_SCALE_TCG` | `5` | Time scale for jme_time_scale_convert. |
| `JME_TIME_SCALE_TCB` | `6` | Time scale for jme_time_scale_convert. |
| `JME_AYANAMSA_MEAN` | `0` | jme_get_ayanamsa_ex2 flag: mean equinox of date. |
| `JME_AYANAMSA_TRUE` | `1` | jme_get_ayanamsa_ex2 flag: true equinox of date (mean + nutation in longitude). |
| `JME_JPL_CENTER_STRICT` | `0` | JPL planet-centre policy: missing planet centre is an error (default). |
| `JME_JPL_CENTER_BARYCENTER` | `1` | JPL planet-centre policy: use the system barycentre when the planet centre is missing (opt-in). |
| `JME_ENGINE_ID_JPL` | `1` | Engine reported by jme_calc_resolve_engine: JPL/CALCEPH. |
| `JME_ENGINE_ID_MOSHIER` | `2` | Engine reported by jme_calc_resolve_engine: Moshier. |
| `JME_ENGINE_ID_VSOP87_ELP82B` | `3` | Engine reported by jme_calc_resolve_engine: VSOP87A + ELP 2000-82B. |
| `JME_MODEL_NUT_IAU_2006A` | `351` | Nutation model: IAU 2000A with IAU 2006 (P03) adjustments (ERFA eraNut06a). |
| `JME_SIDEREAL_LAHIRI_ICRC` | `406` | Sidereal mode: Lahiri (ICRC definition). |
| `JME_MODEL_DELTAT_STEPHENSON_ETC_2021` | `407` | Delta-T model: Morrison, Stephenson, Hohenkerk & Zawilski 2021 (Table S15, 2020 revision); used by AUTOMATIC before the IERS table. |
| `JME_MODEL_DELTAT_MS2004_TABLE1_LINEAR` | `408` | Delta-T model: Morrison & Stephenson 2004 Table 1 with the authors' simple (linear) interpolation; their parabola -20 + 32t^2 outside the table. |

#### Behaviour changes

- Precession model PREC=LASKAR1986 (JME_MODEL_PREC_LASKAR_1986) now returns a matrix (Laskar 1986 Tables 5 and 8) instead of an error.
- JME_MODEL_DELTAT_STEPHENSON_ETC_2016 is now the published 2016 Table S15; JME_TIME_DELTAT_AUTOMATIC uses the 2021 revision before the IERS table.
- With the DE441 tidal selector (jme_set_tid_acc(JME_TIME_TIDAL_DE441)), historical (pre-1955) Delta-T returns NaN and an error naming Park et al. 2021, because no DE441 lunar tidal acceleration has been published. JME_TIME_TIDAL_AUTOMATIC applies no correction.
- The tidal correction is never applied to IERS observed/predicted values or to a user-fixed Delta-T.
- Delta-T models SM1984 and S1997 stay refused with explicit errors (sources unavailable).

