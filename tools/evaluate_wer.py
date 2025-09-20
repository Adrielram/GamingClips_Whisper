"""
Simple WER calculation between two .srt files (reference, hypothesis).
Usage:
python tools/evaluate_wer.py reference.srt hypothesis.srt
"""
import sys
import re
from pathlib import Path

def srt_to_text(path):
    words = []
    with open(path, encoding='utf-8') as f:
        for line in f:
            line=line.strip()
            if not line or re.match(r'^\d+$', line) or re.match(r'^\d{2}:\d{2}:\d{2}', line):
                continue
            # remove punctuation except intra-word apostrophes
            clean = re.sub(r"[^\w\s'áéíóúÁÉÍÓÚñÑüÜ]", '', line)
            words.extend(clean.lower().split())
    return words


def wer(ref_words, hyp_words):
    r = ref_words
    h = hyp_words
    # dp
    import math
    n = len(r)
    m = len(h)
    if n==0:
        return math.inf
    d = [[0]*(m+1) for _ in range(n+1)]
    for i in range(n+1):
        d[i][0]=i
    for j in range(m+1):
        d[0][j]=j
    for i in range(1,n+1):
        for j in range(1,m+1):
            if r[i-1]==h[j-1]:
                d[i][j]=d[i-1][j-1]
            else:
                d[i][j]=1+min(d[i-1][j], d[i][j-1], d[i-1][j-1])
    return d[n][m]/n, d[n][m]

if __name__=='__main__':
    if len(sys.argv)<3:
        print('Usage: python tools/evaluate_wer.py reference.srt hypothesis.srt')
        sys.exit(1)
    ref = srt_to_text(Path(sys.argv[1]))
    hyp = srt_to_text(Path(sys.argv[2]))
    rate, errs = wer(ref,hyp)
    print(f'Reference words: {len(ref)}')
    print(f'Hypothesis words: {len(hyp)}')
    print(f'Errors: {errs}')
    print(f'WER: {rate:.3f}')
