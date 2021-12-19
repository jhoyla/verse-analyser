import csv
import re
import logging
import sys
import itertools
import verselex, verseparser
import manuscriptslex, manuscriptsparser
from verse import Verse
from graphviz import Graph
from os import listdir
from os.path import isfile, join
from functools import reduce
logger = logging.getLogger('default')

# Possible variant types of manuscripts
variants = ['*', 'm', 'a', 'o']
no_of_variants = len(variants)
pair = {'*':'m','m':'*','a':'o', 'o':'a'}

parser = verseparser.build()

# The variant type that of each pair that indicates no change / the original text
default_variants = ['*', 'o']

is_normal = re.compile('^[0-9]+$')
is_special = re.compile('^[0-9]+[m\*ao]$')

def get_base(m):
    if is_special.match(m) == None:
        return m
    else:
        return m[:-1]

def index_manuscripts(manuscripts):
    return {k:v for v,k in enumerate(manuscripts)}


#Takes the number of manuscripts, a depth, and the additive identity, and returns a table of dimensions `|manuscripts| X |manuscripts| X depth` filled with the additive identity
def build_table(no_of_manuscripts, depth, add_id):
    table = [[[add_id for x in range(no_of_manuscripts)] for y in range(no_of_manuscripts)] for z in range(depth)]
    return table

def populate_table(table, oms,  words, exclusions):
    for (word_i, word) in enumerate(words):
        for reading in word:
            for (i_index, m_i) in enumerate(reading):
                if get_base(m_i) in exclusions:
                    continue
                logger.debug('i_index, i: {i_index}, {i}'.format(i_index=i_index, i=m_i))
                for j_index in range(i_index, len(reading)):
                    m_j = reading[j_index]
                    if get_base(m_j) in exclusions:
                        continue
                    logger.debug('j_index, j: {j_index}, {j}'.format(j_index=j_index, j=m_j))

                    exp_mi = []
                    if is_special.match(m_i) == None:
                        exp_mi = ['{base}{dec}'.format(base=m_i, dec=x) for x in variants]
                    else:
                        exp_mi = [m_i]

                    exp_mj = []
                    if is_special.match(m_j) == None:
                        exp_mj = ['{base}{dec}'.format(base=m_j, dec=x) for x in variants]
                    else:
                        exp_mj = [m_j]

                    updates = [(oms[x], oms[y]) for x in exp_mi for y in exp_mj if oms[x] <= oms[y]] 
                    for x,y in updates:
                        try:
                            table[word_i][x][y] += 1
                        except IndexError:
                            logger.warning('IndexError in table: {i}, {x}, {y}'.format(i=word_i, x=x_index, y=y_index))
                            raise IndexError
    return table

def project_table(table, manuscripts):
    proj = [[sum([table[x][y][z] for x in range(len(table))]) for y in range(len(table[0]))] for z in range(len(table[0][0]))]
    
    with open('array_proj.csv', 'w') as fd:
        writer = csv.writer(fd)
        writer.writerow(itertools.chain(['-'], manuscripts.values()))
        for i, row in enumerate(proj):
            writer.writerow(itertools.chain([manuscripts[i]],row))

    return proj

def k_order(edge):
    return -1 * edge[2]

def clean_edges(edges, manuscripts, actuals):
    res = [manuscripts[n] for n in actuals]
    return [(x, y, z) for (x, y, z) in edges if x in res and y in res]


def kruskals(p_table, manuscripts, actuals):
    rough_edges = [(x, y, p_table[x][y]) for x in range(len(p_table)) for y in range(len(p_table)) if p_table[x][y] != 0]
    logger.debug("Rough edges: {re}".format(re=len(rough_edges)))
    edges = clean_edges(rough_edges, manuscripts, actuals)
    logger.debug("Clean edges: {e}".format(e=len(edges)))
    edges.sort(key=k_order)
    ss = [set([x]) for x in [manuscripts[a] for a in actuals]]
    logger.debug("Sets: {ss}".format(ss=ss))
    tree = []

    for edge in edges:
        found_s0 = False
        found_s1 = False
        if len(ss) == 1:
            break
        for s in ss:
            if edge[0] in s:
                s0 = s
                found_s0 = True
            if edge[1] in s:
                s1 = s
                found_s1 = True
            if found_s0 and found_s1:
                break
        if s0 != s1:
            tree.append(edge)
            ss.remove(s0)
            ss.remove(s1)
            ss.append(s0.union(s1))
    return tree

def draw_tree(tree, manuscripts):
    g = Graph(name="Tree")

    logger.debug("Manuscripts length: {ms}".format(ms=len(manuscripts)))
    for manuscript,number in manuscripts.items():
        if manuscript[-1]=='*':
            g.node('m{n}'.format(n=number), manuscript[:-1])
        else:
            g.node('m{n}'.format(n=number), manuscript)
    for edge in tree:
        g.edge('m{a}'.format(a=edge[0]), 'm{b}'.format(b=edge[1]))

    g.format = 'svg'

    g.render('out', view=True)

def get_files(path):
    return [f for f in listdir(path) if isfile(join(path, f))]

def init_parsers():
    man_lexer = manuscriptslex.ManuscriptsLexer()
    man_lexer.build()

    man_parser = manuscriptsparser.build()

    verse_lexer = verselex.VersesLexer()
    verse_lexer.build()
    verse_parser = verseparser.build()
    return man_lexer, man_parser, verse_lexer, verse_parser

def get_actuals(manuscripts, verses):
    # Merge all sets of decorations
    for v in verses:
        logger.debug("Verse: {d}".format(d=v.decorations))
    res = reduce(__merge__, [v.decorations for v in verses], dict())

    logger.debug(res.keys())

    for m,d in res.items():
        d.add('*')

    logger.debug("Manuscripts: {m}".format(m=manuscripts))

    out = []
    for x in res.keys():
        for y in res[x]:
            out.append(x + y)

    return out

def __merge__(a,b):
    res = {}
    bk = list(b.keys())
    for x in a.keys():
        if x in b.keys():
            res[x] = a[x].union(b[x])
            bk.remove(x)
        else:
            res[x] = a[x]
    for x in bk:
        res[x] = b[x]
    return res

def get_ordered_manuscripts(manuscripts):
    oms = []
    for m in manuscripts:
        if is_special.match(m) != None:
            raise SyntaxError("Manuscript should be undecorated: {m}".format(m=m))
        for v in variants:
            oms.append(m + v)

    oms.sort(key=lambda x: (int(x[:-1])*10)+variants.index(x[-1]))
    ioms = index_manuscripts(oms)
    return ioms

def do_run(manuscript_path, verses_path):
    man_lexer, man_parser, verse_lexer, verse_parser = init_parsers()
    with open(manuscript_path, 'r') as fd: 
        man_str = fd.read()

    ms = man_parser.parse(man_str, lexer=man_lexer.lexer)

    verse_files = get_files(verses_path)

    verse_strs = []
    for f in verse_files:
        with open(join(verses_path, f), 'r') as fd:
            verse_strs.append(fd.read())

    p_verses = []
    for vs in verse_strs:
        p_verses.extend(verse_parser.parse(vs, lexer=verse_lexer.lexer))
    verses = [Verse(x[0], x[1], x[2], ms) for x in p_verses] 

    chapter_len = sum([len(x.words) for x in verses])

    ioms = get_ordered_manuscripts(ms)
    oms = {v:k for k,v in ioms.items()}
    t = build_table(len(ioms), chapter_len, 0)

    counter = 0
    for verse in verses:
        logger.debug(counter)
        populate_table(t[counter:counter+len(verse.words)], ioms, verse.words, verse.exclusions)
        counter += len(verse.words)

    p_table = project_table(t, oms)
    logger.debug("Manuscripts length: {ms}".format(ms=len(ioms)))
    actuals = get_actuals(ms, verses)
    tree = kruskals(p_table, ioms, actuals)
    logger.debug("Manuscripts length: {ms}".format(ms=len(ioms)))
    draw_tree(tree, {k:v for k, v in ioms.items() if k in actuals})

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: Path to manuscripts, path to verses")
    else:
        do_run(sys.argv[1], sys.argv[2])
        
