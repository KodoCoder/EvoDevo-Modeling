import numpy as np
import itertools
from my_table import table


def hamming_distance(s1, s2, codon=True):
    if codon:
        s1c, s2c = [], []
        for part in chunker(s1, 3):
            s1c.append(part)
        for part in chunker(s2, 3):
            s2c.append(part)
        return sum(c1 != c2 for c1, c2 in itertools.izip(s1c, s2c))
    else:
        return sum(c1 != c2 for c1, c2 in itertools.izip(s1, s2))


def grouper(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return itertools.izip_longest(*args, fillvalue=fillvalue)


def chunker(seq, size):
    return (seq[pos:pos + size] for pos in xrange(0, len(seq), size))


def calc_H_xy():
    kys = table.keys()
    kys.sort()
    vals = table.values()
    accumy = 0
    for i in kys:
        
