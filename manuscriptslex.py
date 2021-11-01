import ply.lex as lex

class ManuscriptsLexer(object):
    tokens = ['MANUSCRIPT', 'COMMA', 'NEW_LINE']

    def t_MANUSCRIPT(self, t):
        r"\d+[oma*]?"
        return t

    def t_NEW_LINE(self, t):
        r"\n+"
        t.lexer.lineno += len(t.value)
        return t

    literals = ','

    t_ignore = " \t"

    t_COMMA = r","

    def t_error(self, t):
        print("Illegal character '{e}'".format(e=t.value[0]))
        t.lexer.skip(1)

    def build(self, **kwargs):
        self.lexer = lex.lex(object=self, **kwargs)

    def test(self, data):
        self.lexer.input(data)
        for token in self.lexer:
            print(token)
