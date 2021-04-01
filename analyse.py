import csv
import re
import logging
import sys
import verselex, verseparser
import manuscriptslex, manuscriptsparser
from verse import Verse
from graphviz import Graph
from os import listdir
from os.path import isfile, join
from functools import reduce
logger = logging.getLogger('default')

# Possible variant types of manuscripts
variants = ['*', 'm', 'a', '°']
no_of_variants = len(variants)
pair = {'*':'m','m':'*','a':'°', '°':'a'}

parser = verseparser.build()

# The variant type that of each pair that indicates no change / the original text
default_variants = ['*', '°']

is_normal = re.compile('^[0-9]+$')
is_special = re.compile('^[0-9]+[m\*a°]$')

def parse_group(group, actuals):
    # Require each group to be in the correct format
    patt = re.compile('^\s*(([0-9]+[am°\*]?\s*,\s*)*[0-9]+[am°\*]?)?\s*$')
    if patt.match(group) == None:
        raise SyntaxError("Group is not in correct format: {grp}".format(grp=group))

    # Break into tokens
    literal = [x.strip() for x in group.split(',') if x.strip() != '']
    logger.debug("Input group: {ig}".format(ig=literal))

    # The first pass will replace any "normal" / untagged manuscripts with the variants.
    # A second pass will be needed to deal with the case where only a subset of the pairs of variants appear,
    # however this cannot be done at the group level, it must be done at the word level.
    first_pass = []
    for manuscript in literal:
        if is_normal.match(manuscript) != None:
            actuals.add(manuscript + '*')
            # An undecorated manuscript number indicates that all variants are in the same group.
            for variant in variants:
                first_pass.append(manuscript + variant)
        elif is_special.match(manuscript) != None:
            actuals.add(manuscript)
            actuals.add(get_pair(manuscript))
            first_pass.append(manuscript)
        else:
            raise SyntaxError('Bad  manuscript: {man}'.format(man=manuscript))
    logger.debug("First pass readings: {fp}".format(fp=first_pass))
    return first_pass

# parse_file takes a filename and an ordered, decorated list of manuscripts, and returns a list of verses
def parse_file(filename, manuscripts, actuals):
    title_line = re.compile('^\s*[0-9]+,\s*[0-9]+\s*,[0-9]+,\s*[0-9]+\s*$')
    
    lines = []

    with open(filename, 'r') as cr:
        for row in cr:
            if len(row) != 0:
                lines.append(row)


    verses = []
    verse = []
    state_machine = 'a'
    for line in lines:
        if line == '===':
            if len(verse) != 0:
                verses.append(verse)
            verse = []

# parse_verse takes a filename and an ordered, decorated list of manuscripts.
def parse_verse(filename, manuscripts, actuals):
    verse = []
    with open(filename, 'r') as cr:
        i = csv.reader(cr, delimiter='/', quotechar='"')
        for row in i:
            if len(row) != 0:
                verse.append(row)

    # Remove the list of manuscripts to ignore.
    blanks = []
    if verse[-2] == '---' or '\'---':
        logger.debug("Manuscripts need to be ignored.")
        blanks = parse_group(verse[-1][0], set())
        logger.debug("Ignored manuscripts: {im}".format(im=blanks))
        verse = verse[:-2]
    for blank in blanks:
        manuscripts.pop(blank)

    words = []

    # Produce a first pass of the manuscripts
    for word in verse:
        logger.debug("Unparsed word: {wrd}".format(wrd=word))
        if len(word) == 0:
            logger.warning("Dropping empty word. All empty lines should have been dropped by this point.")
            break
        readings = [parse_group(reading, actuals) for reading in word if len(parse_group(reading, set())) > 0  ]
        words.append(readings)

    # Compute the set of manuscripts that were not included
    for word in words:
        ms_stack = list(manuscripts.keys())
        for reading in word:
            for elem in reading:
                if is_special.match(elem) == None:
                    raise SyntaxError('Normal and malformed manuscripts should have been removed by now. {man}'.format(man=elem))
                if elem in blanks:
                    raise SyntaxError('Manuscript {elem} appears in a verse in which it is excluded.'.format(elem=elem))
                if elem not in manuscripts:
                    raise LookupError('Unknown manuscript: {man}'.format(man=elem))
                ms_stack.remove(elem)
        logger.debug("Remaining manuscripts in ms_stack: {rm}".format(rm=ms_stack))
        for remainder in ms_stack:
            logger.debug("Remainder: {rd}".format(rd=remainder))
            if get_pair(remainder) not in ms_stack: 
                logger.debug("\tPair not in ms_stack: {rd}".format(rd=remainder))
                word[-1].append(remainder)
            else:
                logger.debug("\tPair in ms_stack: {rd}".format(rd=remainder))
                base_manuscript = remainder[:-1]
                ms_stack.remove(get_pair(remainder))
                d_remainder = get_default(remainder)
                d_modifier = d_remainder[-1]
                logger.debug("\tDefault remainder: {drd}".format(drd=d_remainder))
                c_default_variants = default_variants.copy()
                logger.debug("\tList of defaults: {ds}".format(ds=c_default_variants))
                c_default_variants.remove(d_modifier)
                success = False
                for dvar in c_default_variants:
                    if success:
                        break
                    search_for = base_manuscript + dvar
                    if base_manuscript + dvar not in ms_stack:
                        for reading in word:
                            if search_for in reading:
                                reading.append(remainder)
                                reading.append(get_pair(remainder))
                                success = True
                                break
                if not success:
                    word[-1].append(remainder)
                    word[-1].append(get_pair(remainder))
        logger.debug("Parsed word: {wrd}".format(wrd=word))


    sanity_check(words, manuscripts)
    return words

def sanity_check(words, manuscripts):
    for word in words:
        ms_stack = list(manuscripts.keys())
        for reading in word:
            for manuscript in reading:
                ms_stack.remove(manuscript)
        assert(len(ms_stack) == 0)


def get_pair(variant):
    base_manuscript = variant[:-1]
    modifier = variant[-1]
    return base_manuscript + pair[modifier]

def get_default(variant):
    modifier = variant[-1]
    if modifier in default_variants:
        return variant
    else:
        return variant[:-1] + pair[modifier]


#Takes a filename and returns the list of manuscripts on the first line of the file.
def parse_manuscripts(filename):
    ms = []
    with open(filename, 'r') as cr:
        i = csv.reader(cr, delimiter=',', quotechar='"')
        for row in i:
            ms.append(row)
    logger.debug("Unparsed manuscripts: {ums}".format(ums=set(ms[0])))
    filtered_ums = list(set(ms[0]))
    filtered_ums.sort()
    for ms in filtered_ums:
        if is_special.match(ms) != None:
            raise SyntaxError("Input manuscripts should be undecorated: {ms}".format(ms=ms))
    dms = []
    for ms in filtered_ums:
        for variant in variants:
            dms.append(ms + variant)
    logger.debug("Decorated manuscripts: {dms}".format(dms=dms))
    return index_manuscripts(dms)


def index_manuscripts(manuscripts):
    return dict(zip(manuscripts, natural_numbers_0()))


#Takes the number of manuscripts, a depth, and the additive identity, and returns a table of dimensions `|manuscripts| X |manuscripts| X depth` filled with the additive identity
def build_table(no_of_manuscripts, depth, add_id):
    table = [[[add_id for x in range(no_of_manuscripts)] for y in range(no_of_manuscripts)] for z in range(depth)]
    return table

def natural_numbers_0():
    num = 0
    while True:
        yield num
        num += 1


def populate_table(table, oms,  words):
    for (word_i, word) in zip(natural_numbers_0(), words):
        for reading in word:
            for (i_index, m_i) in zip(natural_numbers_0(), reading):
                logger.debug('i_index, i: {i_index}, {i}'.format(i_index=i_index, i=m_i))
                for j_index in range(i_index, len(reading)):
                    m_j = reading[j_index]
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

                    updates = [(max(oms[x],oms[y]), min(oms[x], oms[y])) for x in exp_mi for y in exp_mj] 
                    for x,y in updates:
                        try:
                            table[word_i][x][y] += 1
                        except IndexError:
                            logger.warning('IndexError in table: {i}, {x}, {y}'.format(i=word_i, x=x_index, y=y_index))
                            raise IndexError
    return table

def project_table(table):
    proj = [[sum([table[x][y][z] for x in range(len(table))]) for y in range(len(table[0]))] for z in range(len(table[0][0]))]
    return proj

def k_order(edge):
    return -1 * edge[2]

def clean_edges(edges, manuscripts, actuals):
    res = [manuscripts[n] for n in actuals]
    return [(x, y, z) for (x, y, z) in edges if x in res and y in res]


def kruskals(p_table, manuscripts, actuals):
    rough_edges = [(x, y, p_table[x][y]) for x in range(len(p_table)) for y in range(x, len(p_table))]
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

    g.format = 'png'

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
    return man_parser, verse_parser

def get_actuals(manuscripts, verses):
    # Merge all sets of decorations
    res = reduce(__merge__, [v.decorations for v in verses], dict())
    for m in manuscripts:
        res.setdefault(m, set())
    return res

def __merge__(a,b):
    res = {}
    bk = b.keys()
    for x in a.keys():
        if x in b.keys():
            res[x] = a[x].union(b[x])
            bk.remove(x)
        else:
            res[x] = a[x]
    for x in bk:
        res[x] = b[x]
    return res

def do_run(manuscript_path, verses_path):
    man_parser, verse_parser = init_parsers()
    with open(manuscript_path, 'r') as fd: 
        man_str = fd.read()

    ms = man_parser.parse(man_str)

    verse_files = get_files(verses_path)
    verse_strs = []
    for f in verse_files:
        with open(join(verses_path, f), 'r') as fd:
            verse_strs.append(fd.read)

    p_verses = [verse_parser.parse(x) for x in verse_strs]
    verses = [Verse(x[0], x[1], x[2], ms) for x in p_verses] 

    chapter_len = sum([len(x.words) for x in verses])

    t = build_table(len(ms), chapter_len, 0)

    counter = 0
    for verse in verses:
        logger.debug(counter)
        populate_table(t[counter:counter+len(verse.words)],ms,  verse.words)
        counter += len(verse.words)

    p_table = project_table(t)
    logger.debug("Manuscripts length: {ms}".format(ms=len(ms)))
    actuals = get_actuals(ms, verses)
    tree = kruskals(p_table, ms, actuals)
    logger.debug("Manuscripts length: {ms}".format(ms=len(ms)))
    draw_tree(tree, {k:v for k, v in ms.items() if k in actuals})

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: Path to manuscripts, path to verses")
    else:
        do_run(sys.argv[1], sys.argv[2])
        
