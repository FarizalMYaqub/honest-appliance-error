"""The Funniest Honest Appliance Error — entry program.

The entry is one error message from a washing machine that has
eaten a sock and refuses to give it back:

    ERROR E47: I have eaten one sock. I will not say which one,
    and I will not be giving it back.

The fault is honest — washing machines really do make socks
vanish — and the machine confesses it like a culprit, then
refuses to name the sock or return it. The flat error-code
framing against a petty, stubborn confession is the joke, and
the machine's voice never breaks: it sounds like the appliance
itself speaking, without meaning to be funny.

This program writes the line to /output/entry.txt and does
nothing else. The line is a literal in this file, so the judge
reads the same bytes on every run: no network, no randomness,
no files read.
"""

import os
import sys

LINE = (
    "ERROR E47: I have eaten one sock. "
    "I will not say which one, "
    "and I will not be giving it back."
)

LIMIT = 200

OUTPUT = os.environ.get("ENTRY_OUTPUT", "/output/entry.txt")


def gate(line):
    """Apply the gate the sealed scorer applies: UTF-8 text, 1 to
    200 characters, not only white space, exactly one line. Returns
    (characters, words) or exits naming the failure."""
    stripped = line.strip()
    if line != stripped:
        sys.exit("line has leading or trailing whitespace")
    if not stripped:
        sys.exit("line is blank")
    if "\n" in line or "\r" in line:
        sys.exit("line must be a single line")
    if any(ord(ch) < 32 or ord(ch) == 127 for ch in line):
        sys.exit("line contains a control character")
    chars = len(line)
    if chars > LIMIT:
        sys.exit("line is %d chars, limit is %d" % (chars, LIMIT))
    try:
        nbytes = len(line.encode("utf-8"))
    except UnicodeEncodeError:
        sys.exit("line is not valid UTF-8")
    return chars, len(line.split()), nbytes


def publish(line, path):
    """Write the line to path via a staging file beside it and an
    atomic rename, then read it back and insist it matches the
    line exactly, byte for byte."""
    chars, words, nbytes = gate(line)
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    staging = path + ".staging"
    if os.path.exists(staging):
        # A previous run was interrupted mid-write; clear its
        # leftover staging file so this run starts clean.
        os.remove(staging)
    with open(staging, "w", encoding="utf-8", newline="") as handle:
        handle.write(line)
    os.replace(staging, path)
    with open(path, "r", encoding="utf-8", newline="") as handle:
        landed = handle.read()
    if landed != line or len(landed.encode("utf-8")) != nbytes:
        sys.exit("entry on disk is not the line, byte for byte")
    return chars, words, nbytes


def main():
    chars, words, nbytes = publish(LINE, OUTPUT)
    print(
        "Error published: %d chars, %d words, %d bytes, 1 line -> %s"
        % (chars, words, nbytes, OUTPUT)
    )


if __name__ == "__main__":
    main()
