import re
import logging
import functools
import verselex
import verseparser
import manuscriptslex
import manuscriptsparser
import verse as v
logger = logging.getLogger('default')

is_special = re.compile('^[0-9]+[m\*ao]$')
pair = {'*':'m','m':'*','a':'o', 'o':'a'}
variants = ['*', 'm', 'a', 'o']
others = {variant:[alt for alt in variants if alt != variant] for variant in variants}


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

    def validate_data(self):
        pass


    def complete_readings(self, manuscripts):
        # For each word
        for word in self.__owords__:
            # For each reading
            for x, reading in enumerate(word):
                # Build strike list of manuscripts
                ms_set = set(manuscripts)
                # For each manuscript
                for y, manuscript in enumerate(reading):
                    # if manuscript is undecorated
                    if is_special.match(manuscript) == None:
                        # remove the manuscript from the strike list
                        try:
                            ms_set.remove(manuscript)
                        except ValueError:
                            logger.error("Manuscript {m} is not in the strike list".format(m=manuscript))
                    # Otherwise
                    else:
                        # If the decorated manuscript is not in the list
                        if manuscript not in ms_set:
                            for alt in get_others(manuscript):
                                # Add all possible variants to the list of manuscripts
                                ms_set.add(alt)
                            # And try to remove the undecorated manuscript
                            try:
                                ms_set.remove(manuscript[:-1])
                            except:
                                logger.error("Neither {m} nor {dm} is in the strike list".format(m=manuscript[:-1], dm=manuscript))
                        # If the decorated manuscript is already in the manuscript list
                        else:
                                # Other variants have already been added. Remove this one.
                                ms_set.remove(manuscript)

            if len(word) == 0:
                logger.error("No words")
            logger.debug("ms_list: {ms_list}".format(ms_list=list(ms_set)))

            ms_rem = list(ms_set)
            ms_rem.sort(key=lambda x: ((int(x[:-1])*10)+variants.index(x[-1]) if is_special.match(x) != None else int(x)*10))
            if len(word[-1]) == 0:
                word[-1] = ms_rem
            else:
                word.append(ms_rem)




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
            if base in dec_table.keys():
                dec_table[base].add(decoration)
            else:
                dec_table[base] = set(decoration)

        for manuscript in manuscripts:
            try:
                 dec_table[manuscript]
            except KeyError:
                dec_table[manuscript] = set('*')

        for manuscript in self.exclusions:
            dec_table.pop(manuscript)
        return dec_table



    def get_pair(self, variant):
        base_manuscript = variant[:-1]
        modifier = variant[-1]
        return base_manuscript + pair[modifier]


@functools.cache
def get_others(d_manuscript):
    if is_special.match(d_manuscript) == None:
        logger.error("Undecorated manuscript: {m}".format(m=d_manuscript))
        raise (RuntimeError("Undecorated manuscript"))
    base_manuscript = d_manuscript[:-1]
    modifier = d_manuscript[-1]
    return [base_manuscript + alt for alt in others[modifier]]
