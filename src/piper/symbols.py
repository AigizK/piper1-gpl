"""Symbol table for text processing.

This builds `pmap` from ru_dictionary definitions without Kaldi-style
position suffixes ("_I", "_S", "_B", "_E").

Rules:
- Preserve punctuation ids as the first entries.
- Russian vowels are stress-marked: e.g. "a0", "a1".
- Soft letters add a separate "j" token (e.g., "я" -> "j" + "a0/1").
- Consonants include palatalized variants with trailing "j" where applicable.
- Bashkir phones use "*2" tokens from B_VOWELS/B_CONS (no stress/palatalization).
"""

from .baru_dictionary import (
    softhard_cons,
    other_cons,
    vowels,
    B_VOWELS,
    B_CONS,
)

# 1) Fixed punctuation ids (must remain unchanged)
BAKRUS_PHONEME_ID_MAP : dict[str, list[int]] = {
    "_": [0],
    "^": [1],
    "$": [2],
    " ": [3],
    "!": [4],
    "'": [5],
    "(": [6],
    ")": [7],
    ",": [8],
    "-": [9],
    ".": [10],
    ":": [11],
    ";": [12],
    "?": [13],
    '@':[14], # тип предложения Friendly
    "#": [15],# тип предложения Neutral
}

next_id = len(BAKRUS_PHONEME_ID_MAP)

# 2) Russian vowels with stress
vowel_bases = sorted(set(vowels.values()), key=lambda x: ['a', 'e', 'i', 'o', 'u', 'y'].index(x))
for vb in vowel_bases:
    for stress in (0, 1):
        token = f"{vb}{stress}"
        if token not in BAKRUS_PHONEME_ID_MAP:
            BAKRUS_PHONEME_ID_MAP[token] = next_id
            next_id += 1

# 3) Russian 'j' (used standalone: from soft letters and for 'й')
if 'j' not in BAKRUS_PHONEME_ID_MAP:
    BAKRUS_PHONEME_ID_MAP['j'] = next_id
    next_id += 1

# 4) Russian consonants
#    - soft/hard set produces base and palatalized (with trailing 'j')
soft_hard_bases = sorted(set(softhard_cons.values()))
for base in soft_hard_bases:
    for token in (base, f"{base}j"):
        if token not in BAKRUS_PHONEME_ID_MAP:
            BAKRUS_PHONEME_ID_MAP[token] = next_id
            next_id += 1

#    - other consonants as-is (zh, c, ch, sh, sch, j)
for token in sorted(set(other_cons.values())):
    if token not in BAKRUS_PHONEME_ID_MAP:
        BAKRUS_PHONEME_ID_MAP[token] = next_id
        next_id += 1

# 5) Bashkir tokens (no stress/palatalization)
for token in sorted(set(B_VOWELS.values())):
    if token not in BAKRUS_PHONEME_ID_MAP:
        BAKRUS_PHONEME_ID_MAP[token] = next_id
        next_id += 1
for token in sorted(set(B_CONS.values())):
    if token not in BAKRUS_PHONEME_ID_MAP:
        BAKRUS_PHONEME_ID_MAP[token] = next_id
        next_id += 1

# Export symbols list based on pmap insertion order
symbols = list(BAKRUS_PHONEME_ID_MAP.keys())

# Special symbol ids
SPACE_ID = symbols.index(" ")
