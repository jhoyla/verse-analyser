import csv
import re

pair = {'*':'m','m':'*','a':'°', '°':'a'}

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

    is_normal = re.compile('^[0-9]+$')
    is_special = re.compile('^[0-9]+[m\*a°]$')
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

def update_table(table, word):
    pass
