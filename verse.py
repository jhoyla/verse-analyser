import re
import logging
import verselex
import verseparser
import manuscriptslex
import manuscriptsparser
import verse as v
logger = logging.getLogger('default')

is_special = re.compile('^[0-9]+[m\*a°]$')
pair = {'*':'m','m':'*','a':'°', '°':'a'}


def test(input_file, manuscript_file):
    man_lexer = manuscriptslex.ManuscriptsLexer()
    man_lexer.build()
    man_parser = manuscriptsparser.build()
    with open(manuscript_file, 'r') as fd:
        ms_str = fd.read()

    ms = man_parser.parse(ms_str)

    verse_lexer = verselex.VersesLexer()
    verse_lexer.build()
    verse_parser = verseparser.build()

    with open(input_file, 'r') as fd:
        verse_str = fd.read()

    header = '''===\n2 3 1 1\n%%%'''
    n_verse_str = header + verse_str

    verses = verse_parser.parse(n_verse_str)
    verse_p = verses[0]

    verse = v.Verse(verse_p[0], verse_p[1], verse_p[2], ms)
    return verse
    

class Verse(object):
    def __init__(self, title, words, exclusions, manuscripts):
        self.chapter = title[0]
        self.verse = title[1]
        self.subsection = title[2]
        self.corpus = title[3]
        self.words = words
        self.__owords__ = words
        self.exclusions = exclusions
        self.manuscripts = manuscripts
        self.decorations = self.get_decorations(manuscripts)
        self.decorated_manuscripts = self.get_decorated_manuscripts()
        self.complete_readings(manuscripts)


    def complete_readings(self, manuscripts):
        for word in self.__owords__:
            # Build strike list of manuscripts
            ms_set = set(manuscripts)
            # First expand any unexpanded manuscripts
            #x is the reading
            for x in range(len(word)):
                #y is the manuscript
                ys = range(len(word[x]))
                for y in ys:
                    # if manuscript is undecorated
                    if is_special.match(word[x][y]) == None:
                        # and the manuscript should be then
                        if len(self.decorations.setdefault(word[x][y], set())) != 0:
                            # Remove the undecorated manuscript
                            base = word[x].pop(y)
                            # and replace it with all possible decorations.
                            for dec in self.decorations[base]:
                                word[x].append("{b}{d}".format(b=base,d=dec))


            dms_set = self.decorated_manuscripts.copy()
            # Then build a list of missing manuscripts
            logger.debug("dms_set: {dm}".format(dm=dms_set))
            logger.debug("word: {word}".format(word=word))
            for x in range(len(word)):
                ys = range(len(word[x]))
                for y in ys:
                    dms_set.remove(word[x][y])


            if len(word) == 0:
                logger.error("No words")
            logger.debug("ms_list: {ms_list}".format(ms_list=list(dms_set)))

            # And attach it to the end.
            if len(word[-1]) == 0:
                word[-1] = list(dms_set)
            elif len(ms_set) > 0:
                word.append(list(dms_set))


    def get_decorated_manuscripts(self):
        decs = [x for x,y in self.decorations.items() if len(y) != 0]
        only_plain = [x for x in self.manuscripts if x not in decs]
        for dec in decs:
            for decoration in self.decorations[dec]:
                only_plain.append(dec + decoration)

        return only_plain

    def get_decorations(self, manuscripts):
        # Iterate over the words and create a set of already decorated manuscripts
        decorated = set()
        for word in self.__owords__:
            for group in word:
                for manuscript in group:
                    if is_special.match(manuscript):
                        decorated.add(manuscript)

        # Create a set of the pairs of the decorated manuscripts
        extras = set()
        for variant in decorated:
            extras.add(self.get_pair(variant))

        # Merge the two sets
        full = list(decorated.union(extras))
        
        # Create a dictionary mapping manuscripts to the list of decorations
        dec_table = {}
        for manuscript in full:
            base = manuscript[:-1]
            decoration = manuscript[-1]

            decs = dec_table.setdefault(base, set())
            dec_table[base].add(decoration)

        return dec_table
    


    def get_pair(self, variant):
        base_manuscript = variant[:-1]
        modifier = variant[-1]
        return base_manuscript + pair[modifier]


