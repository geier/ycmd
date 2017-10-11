# coding: utf-8

import operator
from collections import defaultdict
import pickle

import notmuch

FILENAME = '/home/cg/markov.pickle'

file = open(FILENAME, 'rb')
alldata = pickle.load(file)
DATA = alldata['data']
COUNTS = alldata['counts']

FACTOR_1_1 = 1
FACTOR_2_1 = 2
FACTOR_2_2 = 2


def unique(items):
    already = set()
    add = already.add
    return [elem for elem in items if not (elem in already or add(elem))]


def clean_tokens(tokens):
    return [token.strip('.,:;!?)(<>') for token in tokens]


def set_markov(tokens):
    for current, next in zip(tokens[:-1], tokens[1:]):
        DATA[1, 1][current][next] += 1
        COUNTS[1, 1][current] += 1
    for previous, current, next in zip(tokens[:-2], tokens[1:-1], tokens[2:]):
        DATA[2, 1][(previous, current)][next] += 1
        COUNTS[2, 1][previous, current] += 1
    for previous, current, next, after in zip(tokens[:-3], tokens[1:-2], tokens[2:-1], tokens[3:]):
        DATA[2, 2][(previous, current)][(next, after)] += 1
        COUNTS[2, 2][previous, current] += 1


def get_markov(tokens):
    tokens = clean_tokens(tokens)
    out = list()
    try:
        tokens_2_2 = sorted(DATA[2, 2][tokens[-2], tokens[-1]].items(), key=operator.itemgetter(1), reverse=True)[:5]
    except (IndexError, KeyError):
        pass
    else:
        factor = COUNTS[2, 2][tokens[-2], tokens[-1]]
        tokens_2_2 = [(' '.join(item), count * FACTOR_2_2 / factor) for item, count in tokens_2_2]
        out.extend(tokens_2_2)

    try:
        tokens_2_1 = sorted(DATA[2, 1][tokens[-2], tokens[-1]].items(), key=operator.itemgetter(1), reverse=True)[:5]
    except (IndexError, KeyError):
        pass
    else:
        factor = COUNTS[2, 1][tokens[-2], tokens[-1]]
        tokens_2_1 = [(item, count * FACTOR_2_1 / factor) for item, count in tokens_2_1]
        out.extend(tokens_2_1)

    try:
        tokens_1_1 = sorted(DATA[1, 1][tokens[-1]].items(), key=operator.itemgetter(1), reverse=True)[:5]
    except (IndexError, KeyError):
        pass
    else:
        factor = COUNTS[1, 1][tokens[-1]]
        tokens_1_1 = [(item, count * FACTOR_1_1 / factor) for item, count in tokens_1_1]
        out.extend(tokens_1_1)

    out = sorted(out, key=operator.itemgetter(1), reverse=True)
    out = unique([item for item, count in out])
    return out
