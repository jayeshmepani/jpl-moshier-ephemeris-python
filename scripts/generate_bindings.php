<?php

declare(strict_types=1);

$root = dirname(__DIR__);
$nativeRoot = getenv('JME_SOURCE_PATH') ?: null;
if ($nativeRoot === null || $nativeRoot === '') {
    foreach ([
        $root . '/../jpl-ephemeris-',
        $root . '/../jpl-ephemeris',
        $root . '/../../jpl-ephemeris-',
        $root . '/../../jpl-ephemeris',
    ] as $candidate) {
        if (is_dir($candidate)) {
            $nativeRoot = $candidate;
            break;
        }
    }
    $nativeRoot ??= $root . '/../../jpl-ephemeris-';
}

$apiReferencePath = $nativeRoot . '/docs/API_REFERENCE.md';
$headerPaths = [
    $nativeRoot . '/include/jme/jme.h',
    $nativeRoot . '/include/jme/jme_extended.h',
];

foreach (array_merge([$apiReferencePath], $headerPaths) as $path) {
    if (!is_file($path)) {
        fwrite(STDERR, "Required native source file not found: {$path}\n");
        exit(1);
    }
}

$apiReference = file_get_contents($apiReferencePath);
preg_match_all('/\|\s*\d+\s*\|\s*`(jme_[A-Za-z0-9_]+)`\s*\|/', $apiReference, $functionMatches);
$trackedFunctions = array_values(array_unique($functionMatches[1]));

$headers = [];
foreach ($headerPaths as $path) {
    $headers[$path] = file_get_contents($path);
}

function normalize_whitespace(string $value): string
{
    return trim((string) preg_replace('/\s+/', ' ', $value));
}

function canonical_type(string $raw, bool $stripName = true): string
{
    $type = trim($raw);
    if ($stripName) {
        $type = (string) preg_replace('/\s*\b[a-zA-Z_][a-zA-Z0-9_]*\s*$/', '', $type);
    }
    $type = normalize_whitespace((string) preg_replace('/\s*\*\s*/', ' * ', $type));
    return trim((string) preg_replace('/\s+/', ' ', $type));
}

function ctypes_type(string $type): string
{
    return match ($type) {
        'void' => 'None',
        'double' => 'c_double',
        'int' => 'c_int',
        'char' => 'c_char',
        'unsigned int' => 'c_uint',
        'size_t' => 'c_size_t',
        'char *', 'const char *' => 'c_char_p',
        'char **', 'const char **', 'const char * const *' => 'POINTER(c_char_p)',
        'double *', 'const double *' => 'POINTER(c_double)',
        'int *', 'const int *' => 'POINTER(c_int)',
        'unsigned int *', 'const unsigned int *' => 'POINTER(c_uint)',
        'size_t *', 'const size_t *' => 'POINTER(c_size_t)',
        default => throw new RuntimeException("Unsupported C type mapping: {$type}"),
    };
}

$functionDeclarations = [];
foreach ($headers as $header) {
    $normalized = preg_replace('!/\*.*?\*/!s', '', $header);
    $normalized = preg_replace('/^\s*#.*$/m', '', $normalized);
    $chunks = explode(';', (string) $normalized);

    foreach ($chunks as $chunk) {
        if (!str_contains($chunk, 'jme_') || !str_contains($chunk, '(')) {
            continue;
        }

        $chunk = normalize_whitespace($chunk);
        if ($chunk === '' || str_starts_with($chunk, 'typedef')) {
            continue;
        }

        if (!preg_match('/^(.*?)\b(jme_[A-Za-z0-9_]+)\s*\((.*)\)$/', $chunk, $match)) {
            continue;
        }

        $name = $match[2];
        $returnType = ctypes_type(canonical_type($match[1], false));
        $argsRaw = trim($match[3]);
        $argTypes = [];

        if ($argsRaw !== '' && $argsRaw !== 'void') {
            foreach (explode(',', $argsRaw) as $arg) {
                $argTypes[] = ctypes_type(canonical_type($arg));
            }
        }

        $functionDeclarations[$name] = [
            'return' => $returnType,
            'args' => $argTypes,
        ];
    }
}

$orderedSignatures = [];
$missingFunctions = [];
foreach ($trackedFunctions as $name) {
    if (!isset($functionDeclarations[$name])) {
        $missingFunctions[] = $name;
        continue;
    }
    $orderedSignatures[$name] = $functionDeclarations[$name];
}

if ($missingFunctions !== []) {
    fwrite(STDERR, "Missing declarations for tracked functions: " . implode(', ', $missingFunctions) . "\n");
    exit(1);
}

$constantOrder = [];
$constantValues = [];

$evaluate = static function (string $expression) use (&$constantValues) {
    $expression = trim($expression);
    if ($expression === '') {
        return 1;
    }
    if (preg_match('/^"(.*)"$/s', $expression, $match)) {
        return stripcslashes($match[1]);
    }

    $resolved = preg_replace_callback(
        '/\bJME_[A-Z0-9_]+\b/',
        static function (array $match) use (&$constantValues) {
            $name = $match[0];
            if (!array_key_exists($name, $constantValues)) {
                throw new RuntimeException("Unknown constant reference: {$name}");
            }
            return is_string($constantValues[$name]) ? var_export($constantValues[$name], true) : (string) $constantValues[$name];
        },
        $expression
    );

    if (!preg_match('~^[0-9A-Za-z_+\-*/%<>&|(). "\']+$~', $resolved)) {
        throw new RuntimeException("Unsafe expression: {$expression}");
    }

    return eval('return ' . $resolved . ';');
};

foreach ($headers as $header) {
    if (preg_match_all('/^\s*#define\s+(JME_[A-Z0-9_]+)(?:[ \t]+([^\r\n]+))?\s*$/m', $header, $defineMatches, PREG_SET_ORDER)) {
        foreach ($defineMatches as $define) {
            $name = $define[1];
            $value = isset($define[2]) ? trim($define[2]) : '';
            $constantValues[$name] = $evaluate($value);
            if (!in_array($name, $constantOrder, true)) {
                $constantOrder[] = $name;
            }
        }
    }

    if (preg_match_all('/typedef\s+enum\s+[^{]*\{(.*?)\}\s*[A-Za-z0-9_]+\s*;/s', $header, $enumMatches, PREG_SET_ORDER)) {
        foreach ($enumMatches as $enumMatch) {
            $entries = explode(',', $enumMatch[1]);
            $nextValue = null;
            foreach ($entries as $entry) {
                $entry = trim((string) preg_replace('!/\*.*?\*/!s', '', $entry));
                if ($entry === '') {
                    continue;
                }
                if (!preg_match('/^(JME_[A-Z0-9_]+)\s*(?:=\s*(.+))?$/s', $entry, $enumEntryMatch)) {
                    continue;
                }

                $name = $enumEntryMatch[1];
                if (isset($enumEntryMatch[2]) && trim($enumEntryMatch[2]) !== '') {
                    $nextValue = $evaluate(trim($enumEntryMatch[2]));
                } elseif ($nextValue === null) {
                    $nextValue = 0;
                } else {
                    $nextValue++;
                }

                $constantValues[$name] = $nextValue;
                if (!in_array($name, $constantOrder, true)) {
                    $constantOrder[] = $name;
                }
            }
        }
    }
}

$constantLines = [];
foreach ($constantOrder as $name) {
    $value = $constantValues[$name];
    $constantLines[] = $name . ' = ' . var_export($value, true);
}

$signatureLines = [];
foreach ($orderedSignatures as $name => $signature) {
    $args = implode(', ', $signature['args']);
    $signatureLines[] = "    " . var_export($name, true) . ": (" . $signature['return'] . ", [" . $args . "]),";
}

$bindings = <<<PY
"""Raw ctypes binding for the JPL Moshier Ephemeris C API."""

from __future__ import annotations

from collections.abc import Iterable
from ctypes import CDLL, POINTER, byref, c_char, c_char_p, c_double, c_int, c_size_t, c_uint, create_string_buffer
from pathlib import Path

from ._loader import find_library, load_calceph_runtime

_SIGNATURES = {
%s
}


class JmeEph:
    """Direct runtime-FFI loader for the native JME shared library."""

    def __init__(self, library_path: str | Path | None = None) -> None:
        self._calceph = load_calceph_runtime()
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
    """Return all configured JME C function names."""

    return _SIGNATURES.keys()


__all__ = [
    "JmeEph",
    "signature_names",
    "byref",
    "create_string_buffer",
    "c_char",
    "c_char_p",
    "c_double",
    "c_int",
    "c_size_t",
    "c_uint",
    "POINTER",
]
PY;

$constants = <<<PY
"""JPL Moshier Ephemeris constants mapped directly from the native JME headers."""

%s
PY;

file_put_contents(
    $root . '/src/jpl_moshier_ephemeris/bindings.py',
    sprintf($bindings, implode("\n", $signatureLines)) . "\n"
);
file_put_contents(
    $root . '/src/jpl_moshier_ephemeris/constants.py',
    sprintf($constants, implode("\n", $constantLines)) . "\n"
);

fwrite(STDOUT, "Generated " . count($orderedSignatures) . " function signatures and " . count($constantOrder) . " constants.\n");
