# Permission from Stephen L. Moshier

This file records the permission given by Stephen L. Moshier to distribute his material in this project under the MIT License. Personal email addresses are omitted.

## Request

- **From:** Jayesh Mepani (Jayesh Patel), maintainer of JPL Moshier Ephemeris (JME).
- **To:** Stephen L. Moshier.
- **Date:** 11 October 2026.
- **Subject:** "Permission request regarding plan404 and AA 5.6".

The request asked for permission to use and redistribute, inside an MIT-licensed project (JME, https://github.com/jayeshmepani/jpl-ephemeris, and its Python, PHP and Dart bindings), the following material:

- the plan404 coefficient tables and GPLAN.C;
- the AA 5.6 lunar tables (mlr404.c and mlat404.c) and the related lunar routines.

It proposed this credit line:

> Portions derived from the work of Stephen L. Moshier, incorporated herein by permission of the author.

It also offered to remove or replace the material if the author preferred that it not be used.

## Reply (verbatim)

- **Received:** 12 October 2026, 03:46 IST (UTC+5:30).

> Hello Jayesh,
>
> Thank you for writing.
>
> You are welcome to distribute the material posted to the net under an MIT license.
>
> Good luck with your project!
> Steve Moshier

## Scope

The permission covers "the material posted to the net": the material Stephen L. Moshier publishes at http://www.moshier.net/. As used in JME, that is:

- **plan404:** the planetary coefficient tables, fitted to JPL DE404, and the GPLAN.C evaluation routines. Used in `src/moshier_full.c` and `src/moshier/plantbl.h`.
- **AA 5.6 / cmoon lunar theory:** the lunar tables mlr404.c and mlat404.c, and the related lunar evaluation routines. Used in `src/moshier/moonlr404.c`, `src/moshier/moonlat404.c` and `src/moshier_moon.c`.

That material is distributed in JME under the MIT License (see `LICENSE`), by permission of the author given on 12 October 2026, with this credit:

> Portions derived from the work of Stephen L. Moshier, incorporated herein by permission of the author.

A screenshot of the email exchange is kept privately by the maintainer and is not published, because it shows personal mail-client details.
