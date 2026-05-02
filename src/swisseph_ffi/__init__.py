"""Pure Python ctypes binding for the Swiss Ephemeris C library."""

from ._loader import SwissEphLibraryNotFoundError, find_library
from .bindings import (
    POINTER,
    SwissEph,
    byref,
    c_char,
    c_char_p,
    c_double,
    c_int,
    create_string_buffer,
    signature_names,
)
from .constants import *

__all__ = [
    "POINTER",
    "SwissEph",
    "SwissEphLibraryNotFoundError",
    "byref",
    "c_char",
    "c_char_p",
    "c_double",
    "c_int",
    "create_string_buffer",
    "find_library",
    "signature_names",
]
__all__ += [name for name in globals() if name.startswith(("SE", "OK", "ERR"))]
