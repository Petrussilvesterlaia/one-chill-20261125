#!/usr/bin/env python3
"""One Line, One Chill — make.fun bounty entry.

Writes a single horror sentence to output/entry.txt, validates it
(1-200 characters, exactly one sentence, not whitespace-only),
and verifies the write by reading the file back byte-for-byte.
"""

import hashlib
import sys
from pathlib import Path

SENTENCE = (
    "I found my own obituary in this morning's paper, dated three days "
    "from now, with one detail wrong: it said I died peacefully, in my "
    "sleep, at home."
)

TERMINATORS = (".", "!", "?")


def validate(text: str) -> list:
    """Return a list of validation errors (empty means valid)."""
    errors = []
    if not text or not text.strip():
        errors.append("entry is empty or whitespace-only")
    if text != text.strip():
        errors.append("entry has leading or trailing whitespace")
    # No control characters at all (no newline, tab, etc.) — the entry
    # must be a single line of printable text.
    bad_controls = sorted({repr(c) for c in text if ord(c) < 32 or ord(c) == 127})
    if bad_controls:
        errors.append(f"entry contains control characters: {', '.join(bad_controls)}")
    if not 1 <= len(text) <= 200:
        errors.append(f"entry is {len(text)} characters (must be 1-200)")
    # Exactly one sentence: exactly one sentence-ending mark, at the end.
    marks = [c for c in text if c in TERMINATORS]
    if len(marks) != 1:
        errors.append(
            f"entry has {len(marks)} sentence-ending marks (must be exactly 1)"
        )
    elif text and text[-1] not in TERMINATORS:
        errors.append("the single sentence-ending mark is not the last character")
    return errors


def main() -> int:
    errors = validate(SENTENCE)
    if errors:
        for error in errors:
            print(f"INVALID: {error}", file=sys.stderr)
        return 1

    out_dir = Path("/output")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "entry.txt"

    data = SENTENCE.encode("utf-8")
    out_path.write_bytes(data)

    # Read-back verification: the file must be byte-identical to the
    # intended sentence — checked three ways (raw bytes, byte length,
    # and SHA-256 digest) so a silent truncation or rewrite cannot pass.
    read_back = out_path.read_bytes()
    if read_back != data:
        print(
            "INVALID: read-back mismatch (file differs from intended entry)",
            file=sys.stderr,
        )
        return 1
    if len(read_back) != len(data):
        print(
            f"INVALID: read-back length {len(read_back)} != expected {len(data)}",
            file=sys.stderr,
        )
        return 1
    if hashlib.sha256(read_back).hexdigest() != hashlib.sha256(data).hexdigest():
        print("INVALID: read-back SHA-256 digest mismatch", file=sys.stderr)
        return 1

    print(f"OK: wrote {len(SENTENCE)} characters to {out_path}")
    print(f"OK: read-back verified (sha256 {hashlib.sha256(data).hexdigest()})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
