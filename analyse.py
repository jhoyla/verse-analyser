import csv

def parse_verse(filename, manuscripts):
    verse = []
    with open(filename, 'r') as cr:
        i = csv.reader(cr, delimiter='/', quotechar='"')
        for row in i:
            verse.append(row)
    readings = []
    for word in verse:
        groups = []
        for group in word:
            groups.append([x.strip() for x in group.split(',')])
        readings.append(groups)
    return readings

def parse_manuscripts(filename):
    ms = []
    with open(filename, 'r') as cr:
        i = csv.reader(cr, delimiter=',', quotechar='"')
        for row in i:
            ms.append(row)
    return ms[0]
