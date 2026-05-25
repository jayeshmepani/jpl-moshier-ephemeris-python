"""Pure Python ctypes binding for the JPL Moshier Ephemeris C library."""

from ._loader import (
    JmeLibraryNotFoundError,
    find_calceph_library,
    find_library,
    load_calceph_runtime,
)
from .bindings import (
    POINTER,
    JmeEph,
    byref,
    c_char,
    c_char_p,
    c_double,
    c_int,
    c_size_t,
    c_uint,
    create_string_buffer,
    signature_names,
)
from .constants import *

__all__ = [
    "POINTER",
    "JmeEph",
    "JmeLibraryNotFoundError",
    "byref",
    "c_char",
    "c_char_p",
    "c_double",
    "c_int",
    "c_size_t",
    "c_uint",
    "create_string_buffer",
    "find_calceph_library",
    "find_library",
    "load_calceph_runtime",
    "signature_names",
]
__all__ += [name for name in globals() if name.startswith(("JME_",))]
