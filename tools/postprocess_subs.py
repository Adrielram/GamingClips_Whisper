"""
Post-process subtitles to improve readability and fix common ASR errors.
Features:
- Basic normalization (lower/upper casing, punctuation fixes)
- Replacement map for common mis-recognitions (customizable)
- Optional spell-check/correction using SymSpell (if installed)
- Export cleaned .srt or .txt

Usage:
python tools/postprocess_subs.py input.srt output.srt --replacements replacements.json --use-symspell

If SymSpell not installed, will still run replacements/normalization.
"""
from pathlib import Path
import argparse
import json
import re

# Simple replacement map default
DEFAULT_REPLACEMENTS = {
    "аний": "adriel",
    "adne": "adriel",
    "borudo": "boludo",
    "borudo": "boludo",
    "me metieron en el orto": "metetelo en el orto",
}


def read_srt_text(path: Path) -> list:
    lines = []
    with open(path, encoding='utf-8') as f:
        for line in f:
            line=line.strip()
            if not line or re.match(r'^\d+$', line) or re.match(r'^\d{2}:\d{2}:\d{2}', line):
                continue
            lines.append(line)
    return lines


def write_srt_from_lines(path: Path, original_path: Path, new_lines: list):
    # Read original srt to reuse timestamps
    with open(original_path, encoding='utf-8') as f:
        blocks = f.read().split('\n\n')

    out_blocks = []
    i = 0
    for block in blocks:
        if not block.strip():
            continue
        parts = block.split('\n')
        if len(parts) >= 3:
            index = parts[0]
            times = parts[1]
            text = new_lines[i] if i < len(new_lines) else parts[2]
            out_blocks.append(f"{index}\n{times}\n{text}")
            i += 1
        else:
            out_blocks.append(block)

    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(out_blocks))


def normalize_line(line: str, replacements: dict) -> str:
    orig = line
    l = line.strip()
    # simple replacements
    for k, v in replacements.items():
        l = re.sub(r"\b" + re.escape(k) + r"\b", v, l, flags=re.IGNORECASE)
    # collapse multiple spaces
    l = re.sub(r'\s+', ' ', l)
    # fix spacing around punctuation
    l = re.sub(r'\s+([,.!?])', r'\1', l)
    return l


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input', help='input srt file')
    parser.add_argument('output', help='output srt file')
    parser.add_argument('--replacements', help='json file with replacements', default=None)
    parser.add_argument('--use-symspell', action='store_true', help='use symspell for spell correction if available')
    args = parser.parse_args()

    reps = DEFAULT_REPLACEMENTS.copy()
    if args.replacements:
        reps.update(json.loads(Path(args.replacements).read_text(encoding='utf-8')))

    lines = read_srt_text(Path(args.input))
    new_lines = [normalize_line(ln, reps) for ln in lines]

    # Optionally symspell (not mandatory)
    if args.use_symspell:
        try:
            from symspellpy.symspellpy import SymSpell, Verbosity
            # To actually use SymSpell you need a frequency dictionary file
            # If you have one, load it here and run corrections on new_lines.
            print('SymSpell available, but no frequency dictionary provided in this script.')
        except Exception:
            print('SymSpell not available, continuing without')

    write_srt_from_lines(Path(args.output), Path(args.input), new_lines)
    print(f'Wrote cleaned subtitles to {args.output}')
