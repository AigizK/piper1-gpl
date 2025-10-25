#!/usr/bin/python
# -- coding: utf-8 --


# Converts an accented vocabulary to dictionary, for example
#
# абстракцион+истов
# абстр+акцию
# абстр+акция
# 
# абстракционистов a0 b s t r a0 k c i0 o0 nj i1 s t o0 v
# абстракцию a0 b s t r a1 k c i0 j u0
# абстракция a0 b s t r a1 k c i0 j a0
#
 
import sys
from typing import List

softletters = set(u"яёюиье")
startsyl = set(u"#ъьаяоёуюэеиы-")
others = set(["#", "+", "-", u"ь", u"ъ"])

softhard_cons = {
    u"б" : u"b",
    u"в" : u"v",
    u"г" : u"g",
    u"Г" : u"g",
    u"д" : u"d",
    u"з" : u"z",
    u"к" : u"k",
    u"л" : u"l",
    u"м" : u"m",
    u"н" : u"n",
    u"п" : u"p",
    u"р" : u"r",
    u"с" : u"s",
    u"т" : u"t",
    u"ф" : u"f",
    u"х" : u"h"
}

other_cons = {
    u"ж" : u"zh",
    u"ц" : u"c",
    u"ч" : u"ch",
    u"ш" : u"sh",
    u"щ" : u"sch",
    u"й" : u"j"
}
                                
vowels = {
    u"а" : u"a",
    u"я" : u"a",
    u"у" : u"u",
    u"ю" : u"u",
    u"о" : u"o",
    u"ё" : u"o",
    u"э" : u"e",
    u"е" : u"e",
    u"и" : u"i",
    u"ы" : u"y",
}

# -----------------------------
# Bashkir support (b_ prefix)
# -----------------------------

# Treat presence of any of these letters as Bashkir text
BASHKIR_SPECIAL = set(list("әөүғҡңһҙҫ"))
BASHKIR_FORCE = False

# Map Bashkir letters (including shared Russian letters) to *2-style tokens
# Vowels (no stress distinction in Bashkir)
B_VOWELS = {
    u"а": "a2",
    u"ә": "ae2",
    u"о": "o2",
    u"ө": "oe2",
    u"у": "u2",
    u"ү": "ue2",
    u"ы": "y2",
    u"и": "i2",
    u"э": "e2",
}
# Consonants (':2' suffix denotes Bashkir variant)
B_CONS = {
    u"б": "b2",
    u"в": "v2",
    u"г": "g2",
    u"ғ": "gh2",
    u"д": "d2",
    u"ж": "zh2",
    u"з": "z2",
    u"ҙ": "zz2",
    u"й": "j2",
    u"к": "k2",
    u"ҡ": "q2",
    u"л": "l2",
    u"м": "m2",
    u"н": "n2",
    u"ң": "ng2",
    u"п": "p2",
    u"р": "r2",
    u"с": "s2",
    u"ҫ": "s2",
    u"т": "t2",
    u"ф": "f2",
    u"х": "h2",
    u"һ": "hh2",
    u"ц": "c2",
    u"ч": "ch2",
    u"ш": "sh2",
    u"щ": "sch2",
    # Context-dependent semivowels (set in preprocessing)
    u"U": "w2",    # from 'у' near vowels
    u"Y": "wf2",   # from 'ү' near vowels (fronted rounded)
}

B_DROP = set([u"ь", u"ъ"])  # drop


KIR_VOWELS = set(list("аәоөуүыиэеёюя"))


def _preprocess_bashkir_word(word: str) -> str:
    """Apply Bashkir orthographic rules:
    - word-initial 'е' -> 'йэ', otherwise 'е' -> 'э'
    - context semivowels: 'у'/'ү' near a vowel -> 'U'/'Y' markers
    """
    if not word:
        return word
    res = []
    for i, ch in enumerate(word):
        if ch == "е":
            if i == 0:
                res.extend(["й", "э"])  # ЙЭ
            else:
                res.append("э")
        else:
            res.append(ch)
    # After 'е' replacement, mark semivowels for у/ү
    tmp = res
    res2: List[str] = []
    for i, ch in enumerate(tmp):
        if ch in ("у", "ү"):
            left_v = (i - 1 >= 0 and tmp[i - 1] in KIR_VOWELS)
            right_v = (i + 1 < len(tmp) and tmp[i + 1] in KIR_VOWELS)
            if left_v or right_v:
                res2.append("U" if ch == "у" else "Y")
                continue
        res2.append(ch)



    return ("".join(res2)
            .replace("я","йа")
            .replace("ю","йу")
            .replace("ё","йо")
            )


def convert_bashkir(word: str) -> str:
    """Convert a Bashkir word to space-separated b_* phones (no stress)."""
    norm = _preprocess_bashkir_word(word)
    phones: List[str] = []
    for ch in norm:
        if ch in B_DROP or ch in others:
            continue
        if ch in B_VOWELS:
            phones.append(B_VOWELS[ch])
            continue
        if ch in B_CONS:
            phones.append(B_CONS[ch])
            continue
        # Fallback: keep as-is if already b_* or known ascii token
        phones.append(ch)
    return phones

def pallatize(phones):
    for i, phone in enumerate(phones[:-1]):
        if phone[0] in softhard_cons:
            if phones[i+1][0] in softletters:
                phones[i] = (softhard_cons[phone[0]] + "j", 0)
            else:
                phones[i] = (softhard_cons[phone[0]], 0)
        if phone[0] in other_cons:
            phones[i] = (other_cons[phone[0]], 0)

def convert_vowels(phones):
    new_phones = []
    prev = ""
    for phone in phones:
        if prev in startsyl:
            if phone[0] in set(u"яюеё"):
                new_phones.append("j")
        if phone[0] in vowels:
            new_phones.append(vowels[phone[0]] + str(phone[1]))
        else:
            new_phones.append(phone[0])
        prev = phone[0]

    return new_phones

def convert(stressword, lang):
    # Bashkir path: if forced or contains any Bashkir-specific letters, use Bashkir converter
    if lang=="ba":
        return convert_bashkir(stressword.replace("+", ""))

    phones = ("#" + stressword + "#")


    # Assign stress marks
    stress_phones = []
    stress = 0
    for phone in phones:
        if phone == "+":
            stress = 1
        else:
            stress_phones.append((phone, stress))
            stress = 0

    # Pallatize
    pallatize(stress_phones)

    # Assign stress
    phones = convert_vowels(stress_phones)

    # Filter
    phones = [x for x in phones if x not in others]

    return phones