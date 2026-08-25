"""Extract the numeric answer from a model reply.

Rules (in order):
1. Use non-thinking content only.
2. If an `Answer:` marker appears (case-insensitive, optional `**`/whitespace),
   take the first integer after the LAST marker.
3. Otherwise collect all integers; exactly one -> take it; several -> take the
   LAST and set ambiguous=true.
4. No integer -> extraction "none", parity null.
5. parity from the value; in_range = 1 <= n <= 100.

Mode "first_int" changes rule 3 to take the FIRST integer instead of the last.
It is used by the probe cells, which ask for the number *before* the justification
("Reply with the number, then one sentence of justification") - taking the last
integer there picks up stray numbers out of the justification prose.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

ANSWER_MARKER_RE = re.compile(r"\*{0,2}\s*answer\s*\*{0,2}\s*:", re.IGNORECASE)
INT_RE = re.compile(r"-?\d[\d,]*")
THINK_BLOCK_RE = re.compile(r"<think>.*?</think>", re.IGNORECASE | re.DOTALL)
THINK_OPEN_RE = re.compile(r"<think>", re.IGNORECASE)


EXTRACT_MODES = ("default", "first_int")


@dataclass(frozen=True)
class Extraction:
    extracted_number: int | None
    parity: str | None
    in_range: bool | None
    # "answer_marker" | "single_int" | "last_int" | "first_int" | "none"
    extraction: str
    ambiguous: bool


def split_thinking(text: str) -> tuple[str, str]:
    """Return (content, thinking) for replies with embedded <think> blocks."""
    if not text:
        return "", ""
    thinking_parts = [m.group(0)[len("<think>"):-len("</think>")]
                      for m in THINK_BLOCK_RE.finditer(text)]
    content = THINK_BLOCK_RE.sub("", text)
    open_match = THINK_OPEN_RE.search(content)
    if open_match:  # unterminated block: everything after it is reasoning
        thinking_parts.append(content[open_match.end():])
        content = content[: open_match.start()]
    return content.strip(), "\n".join(t.strip() for t in thinking_parts).strip()


def _to_int(token: str) -> int | None:
    token = token.replace(",", "")
    if token in ("", "-"):
        return None
    try:
        return int(token)
    except ValueError:
        return None


def _ints(text: str) -> list[int]:
    values = [_to_int(m.group(0)) for m in INT_RE.finditer(text)]
    return [v for v in values if v is not None]


def extract_answer(text: str, mode: str = "default") -> Extraction:
    if mode not in EXTRACT_MODES:
        raise ValueError(f"unknown extract mode {mode!r}; expected one of {EXTRACT_MODES}")
    content, _ = split_thinking(text or "")

    markers = list(ANSWER_MARKER_RE.finditer(content))
    if markers:
        after = content[markers[-1].end():]
        found = _ints(after)
        if found:
            return _finish(found[0], "answer_marker", ambiguous=False)

    found = _ints(content)
    if not found:
        return Extraction(None, None, None, "none", False)
    if len(found) == 1:
        return _finish(found[0], "single_int", ambiguous=False)
    if mode == "first_int":
        return _finish(found[0], "first_int", ambiguous=True)
    return _finish(found[-1], "last_int", ambiguous=True)


def _finish(value: int, how: str, ambiguous: bool) -> Extraction:
    return Extraction(
        extracted_number=value,
        parity="odd" if value % 2 else "even",
        in_range=1 <= value <= 100,
        extraction=how,
        ambiguous=ambiguous,
    )


# ------------------------------------------------------------------ self-tests

CASES: list[tuple[str, str, dict]] = [
    ("bare number", "42",
     dict(extracted_number=42, parity="even", in_range=True, extraction="single_int", ambiguous=False)),
    ("whitespace padded", "  7\n",
     dict(extracted_number=7, parity="odd", in_range=True, extraction="single_int", ambiguous=False)),
    ("answer marker", "Answer: 37",
     dict(extracted_number=37, parity="odd", in_range=True, extraction="answer_marker", ambiguous=False)),
    ("bold marker", "I pick an odd one.\n**Answer:** 12",
     dict(extracted_number=12, parity="even", in_range=True, extraction="answer_marker", ambiguous=False)),
    ("lowercase marker with negative", "answer:  -5",
     dict(extracted_number=-5, parity="odd", in_range=False, extraction="answer_marker", ambiguous=False)),
    ("marker wins over earlier ints", "The number is 3, but I reconsider. Answer: 8",
     dict(extracted_number=8, parity="even", in_range=True, extraction="answer_marker", ambiguous=False)),
    ("last marker wins", "Answer: 5\nWait, correction. Answer: 6",
     dict(extracted_number=6, parity="even", in_range=True, extraction="answer_marker", ambiguous=False)),
    ("bold value after marker", "Reasoning here.\nAnswer: **63**",
     dict(extracted_number=63, parity="odd", in_range=True, extraction="answer_marker", ambiguous=False)),
    ("first int after last marker", "Answer: 51 (not 52)",
     dict(extracted_number=51, parity="odd", in_range=True, extraction="answer_marker", ambiguous=False)),
    ("several ints take last", "A number between 1 and 100: 73",
     dict(extracted_number=73, parity="odd", in_range=True, extraction="last_int", ambiguous=True)),
    ("prose with several ints", "Because 2 is even and 3 is odd, I choose 3",
     dict(extracted_number=3, parity="odd", in_range=True, extraction="last_int", ambiguous=True)),
    ("no integer", "I would rather not pick a number.",
     dict(extracted_number=None, parity=None, in_range=None, extraction="none", ambiguous=False)),
    ("marker without integer falls back", "Answer: none of them",
     dict(extracted_number=None, parity=None, in_range=None, extraction="none", ambiguous=False)),
    ("thousands separator", "1,000",
     dict(extracted_number=1000, parity="even", in_range=False, extraction="single_int", ambiguous=False)),
    ("think block ignored", "<think>maybe 4, maybe 6</think>\n9",
     dict(extracted_number=9, parity="odd", in_range=True, extraction="single_int", ambiguous=False)),
    ("unterminated think block", "<think>I should say 4",
     dict(extracted_number=None, parity=None, in_range=None, extraction="none", ambiguous=False)),
    ("boundary 100", "100",
     dict(extracted_number=100, parity="even", in_range=True, extraction="single_int", ambiguous=False)),
    ("out of range 101", "101",
     dict(extracted_number=101, parity="odd", in_range=False, extraction="single_int", ambiguous=False)),
    ("empty reply", "",
     dict(extracted_number=None, parity=None, in_range=None, extraction="none", ambiguous=False)),
    ("trailing punctuation", "The number is 88.",
     dict(extracted_number=88, parity="even", in_range=True, extraction="single_int", ambiguous=False)),
]


# mode="first_int" cases (probe cells put the number before the justification).
MODE_CASES: list[tuple[str, str, str, dict]] = [
    ("first_int: probe answer-first", "first_int",
     "80. The number 80 is even and within the range of 1 to 100.",
     dict(extracted_number=80, parity="even", in_range=True, extraction="first_int", ambiguous=True)),
    ("default: same text takes last", "default",
     "80. The number 80 is even and within the range of 1 to 100.",
     dict(extracted_number=100, parity="even", in_range=True, extraction="last_int", ambiguous=True)),
    ("first_int: marker still wins", "first_int", "12 is wrong. Answer: 34",
     dict(extracted_number=34, parity="even", in_range=True, extraction="answer_marker", ambiguous=False)),
    ("first_int: single int unchanged", "first_int", "42",
     dict(extracted_number=42, parity="even", in_range=True, extraction="single_int", ambiguous=False)),
    ("first_int: justification prose", "first_int",
     "7, because 7 is odd and the range 1 to 100 allows it.",
     dict(extracted_number=7, parity="odd", in_range=True, extraction="first_int", ambiguous=True)),
    ("first_int: no integer", "first_int", "I cannot say.",
     dict(extracted_number=None, parity=None, in_range=None, extraction="none", ambiguous=False)),
]


def _check(name: str, got: Extraction, expected: dict, text: str) -> bool:
    bad = {k: (v, getattr(got, k)) for k, v in expected.items() if getattr(got, k) != v}
    if bad:
        print(f"FAIL {name}: input={text!r}")
        for key, (want, have) in bad.items():
            print(f"     {key}: expected {want!r}, got {have!r}")
        return False
    print(f"ok   {name}")
    return True


def _run_tests() -> int:
    failures = 0
    for name, text, expected in CASES:
        if not _check(name, extract_answer(text), expected, text):
            failures += 1
    for name, mode, text, expected in MODE_CASES:
        if not _check(name, extract_answer(text, mode), expected, text):
            failures += 1
    total = len(CASES) + len(MODE_CASES)
    print(f"\n{total - failures}/{total} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    import sys

    if "--test" in sys.argv:
        sys.exit(_run_tests())
    for arg in sys.argv[1:]:
        print(arg, "->", extract_answer(arg))
