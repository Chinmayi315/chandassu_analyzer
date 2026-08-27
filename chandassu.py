"""
Kannada Chandassu (Prosody) Analyzer — core logic.

Classifies Kannada text into syllables and assigns each a metrical weight:
  1 = Laghu (short)
  2 = Guru (long)

Then checks whether a 4-line poem matches the Kanda Padya matra pattern
(12-20-12-20).

This is the same rule-based algorithm from the original notebook
(kanda_padya_chandassu.ipynb), refactored to return structured data
instead of printing, so it can be served over an API.
"""

import unicodedata

HALANT = "್"
ANUSVARA = "ಂ"
VISARGA = "ಃ"

LAGHU_SIGNS = ["ಿ", "ು", "ೃ", "ೆ", "ೊ"]
GURU_SIGNS = ["ಾ", "ೀ", "ೂ", "ೇ", "ೈ", "ೋ", "ೌ"]

LAGHU_VOWELS = ["ಅ", "ಇ", "ಉ", "ಋ", "ಎ", "ಒ"]
GURU_VOWELS = ["ಆ", "ಈ", "ಊ", "ಏ", "ಐ", "ಓ", "ಔ"]

KANNADA_CONSONANTS = [chr(i) for i in range(0x0C95, 0x0CB9 + 1)]

KANDA_PADYA_PATTERN = [12, 20, 12, 20]


def analyze_syllables(text: str) -> tuple[list[tuple[str, int]], int]:
    """
    Break Kannada text into syllables and assign Laghu/Guru weights.

    Returns:
        (syllables, total_matra) where syllables is a list of
        (syllable_text, weight) tuples.
    """
    text = unicodedata.normalize("NFC", text)

    i = 0
    total = 0
    syllables: list[tuple[str, int]] = []

    while i < len(text):
        char = text[i]

        if char == " ":
            i += 1
            continue

        # Independent vowels
        if char in LAGHU_VOWELS:
            syllables.append((char, 1))
            i += 1
            continue

        if char in GURU_VOWELS:
            syllables.append((char, 2))
            i += 1
            continue

        # Consonant syllable
        if char in KANNADA_CONSONANTS:
            syllable = char
            weight = 1
            i += 1

            # Attach halant clusters before vowel
            while i < len(text) - 1 and text[i] == HALANT:
                syllable += text[i] + text[i + 1]
                i += 2
                weight = 2

            # Attach vowel sign
            if i < len(text) and text[i] in LAGHU_SIGNS:
                syllable += text[i]
                weight = 1
                i += 1
            elif i < len(text) and text[i] in GURU_SIGNS:
                syllable += text[i]
                weight = 2
                i += 1

            # Anusvara / Visarga
            if i < len(text) and text[i] in [ANUSVARA, VISARGA]:
                syllable += text[i]
                weight = 2
                i += 1

            # Attach vowel sign (again, mirrors original logic)
            if i < len(text) and text[i] in LAGHU_SIGNS:
                syllable += text[i]
                weight = 1
                i += 1
            elif i < len(text) and text[i] in GURU_SIGNS:
                syllable += text[i]
                weight = 2
                i += 1

            # Attach ALL trailing halant clusters (e.g. ಳ್ಳಲ್ case)
            while (
                i < len(text) - 1
                and text[i] in KANNADA_CONSONANTS
                and text[i + 1] == HALANT
            ):
                syllable += text[i] + text[i + 1]
                weight = 2
                i += 2

            # Attach final closing consonant (e.g. ಯೊಳ್ case)
            if (
                i < len(text) - 1
                and text[i] in KANNADA_CONSONANTS
                and text[i + 1] == HALANT
            ):
                syllable += text[i] + text[i + 1]
                weight = 2
                i += 2

            # Ignore pure trailing consonant clusters like ಳಲ್
            if not (len(syllable) <= 2 and syllable.endswith(HALANT)):
                syllables.append((syllable, weight))

            continue

        i += 1

    # Prosody rule adjustment:
    # Laghu becomes Guru if the next syllable begins with a consonant cluster.
    adjusted: list[tuple[str, int]] = []
    for idx, (syll, wt) in enumerate(syllables):
        if wt == 1 and idx + 1 < len(syllables):
            next_syll = syllables[idx + 1][0]
            if HALANT in next_syll[:2]:
                wt = 2
        adjusted.append((syll, wt))

    for _, wt in adjusted:
        total += wt

    return adjusted, total


def check_kanda_padya(lines: list[str]) -> dict:
    """
    Given exactly 4 lines of a poem, analyze each line and check whether
    the matra counts match the Kanda Padya pattern (12-20-12-20).
    """
    if len(lines) != 4:
        raise ValueError("Kanda Padya check requires exactly 4 lines.")

    line_results = []
    counts = []
    for line in lines:
        syllables, total = analyze_syllables(line)
        counts.append(total)
        line_results.append(
            {
                "line": line,
                "matra_count": total,
                "syllables": [{"text": s, "weight": w} for s, w in syllables],
            }
        )

    is_kanda_padya = counts == KANDA_PADYA_PATTERN

    return {
        "lines": line_results,
        "matra_counts": counts,
        "expected_pattern": KANDA_PADYA_PATTERN,
        "is_kanda_padya": is_kanda_padya,
    }
