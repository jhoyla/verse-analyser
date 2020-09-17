import csv
import re
import logging
from graphviz import Graph
from os import listdir
from os.path import isfile, join
logger = logging.getLogger('default')

# Possible variant types of manuscripts
variants = ['*', 'm', 'a', '°']
no_of_variants = len(variants)+1
pair = {'*':'m','m':'*','a':'°', '°':'a'}

# The variant type that of each pair that indicates no change / the original text
default_variants = ['*', '°']

is_normal = re.compile('^[0-9]+$')
is_special = re.compile('^[0-9]+[m\*a°]$')

def parse_group(group):
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
            # An undecorated manuscript number indicates that all variants are in the same group.
            for variant in variants:
                first_pass.append(manuscript + variant)
        elif is_special.match(manuscript) != None:
            first_pass.append(manuscript)
        else:
            raise SyntaxError('Bad  manuscript: {man}'.format(man=manuscript))
    logger.debug("First pass readings: {fp}".format(fp=first_pass))
    return first_pass

# parse_verse takes a filename and an ordered, decorated list of manuscripts.
def parse_verse(filename, manuscripts):
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
        blanks = parse_group(verse[-1][0])
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
        readings = [parse_group(reading) for reading in word if len(parse_group(reading)) > 0  ]
        words.append(readings)

    # Compute the set of manuscripts that were not included
    for word in words:
        ms_stack = list(manuscripts.keys())
        for reading in word:
            for elem in reading:
                if is_special.match(elem) == None:
                    raise SyntaxError('Normal and malformed manuscripts should have been removed by now. {man}'.format(man=elem))
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


def ms_order(man):
    logger.warning('{man}'.format(man=man))
    if is_special.match(man) == None:
        return int(man)*no_of_variants
    else:
        return int(man[:-1])*no_of_variants+variants.index(man[-1])+1

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
                    x_index = max(oms[m_i], oms[m_j])
                    y_index = min(oms[m_i], oms[m_j])
                    try:
                        table[word_i][x_index][y_index] += 1
                    except IndexError:
                        logger.warning('IndexError in table: {i}, {x}, {y}'.format(i=word_i, x=x_index, y=y_index))
                        raise IndexError

    return table

def project_table(table):
    proj = [[sum([table[x][y][z] for x in range(len(table))]) for y in range(len(table[0]))] for z in range(len(table[0][0]))]
    return proj

def update_table(table, word):
    pass
    for reading in word:
        cread = reading.copy()
        cread.sort(key=ms_order)

def k_order(edge):
    return 1/(edge[2]+0.00001)

def kruskals(p_table, manuscripts):
    edges = [(x, y, p_table[x][y]) for y in range(len(p_table)) for x in range(y)]
    edges.sort(key=k_order)
    ss = [set([x]) for x in range(len(p_table))]
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

    for manuscript,number in manuscripts.items():
        g.node('m{n}'.format(n=number), manuscript)
    for edge in tree:
        g.edge('m{a}'.format(a=edge[0]), 'm{b}'.format(b=edge[1]))

    g.format = 'png'

    g.render('out', view=True)

def get_files(path):
    return [f for f in listdir(path) if isfile(join(path, f))]

def do_run(manuscript_path, verses_path):
    ms = parse_manuscripts(manuscript_path)
    verse_files = get_files(verses_path)
    verses = []
    for f in verse_files:
        verses.append(parse_verse(join(verses_path, f), ms.copy()))

    chapter_len = sum(map(len, verses))

    t = build_table(len(ms), chapter_len, 0)

    counter = 0
    for verse in verses:
        logger.warning(counter)
        populate_table(t[counter:counter+len(verse)],ms,  verse)
        counter += len(verse)

    p_table = project_table(t)

    tree = kruskals(p_table, ms)

    draw_tree(tree, ms)
