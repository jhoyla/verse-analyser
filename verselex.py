import ply.lex as lex

class VersesLexer(object):
    tokens = ['VERSE_SEP', 'TITLE_SEP', 'EXCL_SEP', 'NUMBER', 'COMMA', 'MANUSCRIPT', 'SLASH', 'NEW_LINE']
    states = (
            ('header','exclusive'),
            ('body','inclusive'),
            )

    def t_ANY_VERSE_SEP(self, t):
        r"==="
        t.lexer.begin('header')
        return t

    def t_ANY_TITLE_SEP(self, t):
        r"%%%"
        t.lexer.begin('body')
        return t

    t_ANY_EXCL_SEP = r"---"
    t_ANY_COMMA = r","
    def t_body_MANUSCRIPT(self, t):
        r"\d+[°ma*]?"
        return t

    t_ANY_SLASH = r"/"

    def t_header_NUMBER(self, t):
      r"\d+"
      t.value = int(t.value)
      return t

    def t_ANY_NEW_LINE(self, t):
      r"\n+"
      t.lexer.lineno += len(t.value)
      return t

    t_ANY_ignore = " \t"

    literals = ",/"

    def t_ANY_error(self, t):
      print("Illegal character '{e}'".format(e=t.value[0]))
      t.lexer.skip(1)

    def build(self, **kwargs):
        self.lexer = lex.lex(object=self, debug=0, **kwargs)

    def test(self, data):
        self.lexer.input(data)
        for token in self.lexer:
            print(token)
