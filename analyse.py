import csv
import re

variants = ['*', 'm', 'a', '°']
no_of_variants = len(variants)+1
pair = {'*':'m','m':'*','a':'°', '°':'a'}
is_normal = re.compile('^[0-9]+$')
is_special = re.compile('^[0-9]+[m\*a°]$')

def parse_group(group):
    patt = re.compile('^\s*(([0-9]+[am°\*]?\s*,\s*)*[0-9]+[am°\*]?)?\s*$')
    if patt.match(group) == None:
        raise SyntaxError("Group is not in correct format: {grp}".format(grp=group))
    return [x.strip() for x in group.split(',') if x.strip() != '']

def parse_verse(filename, manuscripts):
    verse = []
    with open(filename, 'r') as cr:
        i = csv.reader(cr, delimiter='/', quotechar='"')
        for row in i:
            verse.append(row)
    blanks = []
    if verse[-2] == '---' or '\'---':
        blanks = parse_group(verse[-1][0])
        verse = verse[:-2]
    for blank in blanks:
        manuscripts.remove(blank)

    words = []

    for word in verse:
        readings = [parse_group(reading) for reading in word if len(parse_group(reading)) > 0  ]
        words.append(readings)

    for word in words:
        ms_stack = manuscripts.copy()
        for reading in word:
            for elem in reading:
                if is_normal.match(elem) == None:
                    if is_special.match(elem) == None:
                        raise SyntaxError('Bad manuscript: {man}'.format(man=elem))
                    else:
                        base_manuscript = elem[:-1]
                        modifier = elem[-1]
                        if base_manuscript not in manuscripts:
                            raise LookupError('Unknown manuscript: {man}'.format(man=elem))
                        ms_stack.remove(base_manuscript)
                        pair_manuscript = base_manuscript + pair[modifier]
                        ms_stack.add(pair_manuscript)
                else:
                    ms_stack.remove(elem)
        word.append(list(ms_stack))
    return words        


def parse_manuscripts(filename):
    ms = []
    with open(filename, 'r') as cr:
        i = csv.reader(cr, delimiter=',', quotechar='"')
        for row in i:
            ms.append(row)
    return set(ms[0])


def ms_order(man):
    if is_special.match(man) == None:
        return int(man)*no_of_variants
    else:
        return int(man[:-1])*no_of_variants+variants.index(man[-1])+1

def build_table(words):
    manuscripts = set()
    for a in words:
        for b in a:
            for c in b:
                manuscripts.add(c)
    m_list = list(manuscripts)
    m_list.sort(key=ms_order)
    table = [[[0 for x in m_list] for y in m_list] for z in words]
    return table

def natural_numbers_0():
    num = 0
    while True:
        yield num
        num += 1


def populate_table(table, oms,  words):
    for (word_i, word) in zip(natural_numbers_0(), words):
        for group in word:
            cgroup = group.copy()
            cgroup.sort(key=ms_order)
            for i in range(0, len(cgroup)):
                for j in range(i, len(cgroup)):
                    table[word_i][oms.index(cgroup[i])][oms.index(cgroup[j])] += 1
    return table

def project_table(table):
    proj = [[sum([table[x][y][z] for x in range(len(table))]) for y in range(len(table[0]))] for z in range(len(table[0][0]))]
    return proj

def update_table(table, word):
    pass
