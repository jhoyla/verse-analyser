import ply.yacc as yacc
from verselex import VersesLexer 
tokens = VersesLexer.tokens

def p_verses(p):
    '''verses : emptylist
    | verse_frame verses'''
    if len(p) == 1:
        p[0] = []
    elif len(p) == 2:
        p[0] = [p[1]]
    elif p[2] == [[]]:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[2]

def p_verse_frame(p):
    '''verse_frame : title verse
    | title verse exclusions'''
    if len(p) == 3:
        p[0] = (p[1], p[2], [])
    else:
        p[0] = (p[1], p[2], p[3])

def p_title(p):
    'title : VERSE_SEP NEW_LINE NUMBER NUMBER NUMBER NUMBER NEW_LINE'
    p[0] = (p[3], p[4], p[5], p[6])

def p_verse(p):
    'verse : TITLE_SEP NEW_LINE words NEW_LINE'
    p[0] = p[3]

def p_words(p):
    '''words : readings NEW_LINE EXCL_SEP
    | readings NEW_LINE words'''
    if p[3] == '---':
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]

def p_readings(p):
    '''readings : man_list
    | man_list SLASH readings'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = [p[1]] + p[3]

def p_man_list(p):
    '''man_list : emptylist
    | MANUSCRIPT
    | MANUSCRIPT COMMA man_list'''
    if len(p) == 2 and len(p[1]) == 0:
        p[0] = p[1]
    elif len(p) == 2 and len(p[1]) > 0:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]

def p_empty_list(p):
    'emptylist : '
    p[0] = []

def p_exclusions(p):
    '''exclusions : man_list NEW_LINE'''
    p[0] = p[1]


def p_error(p):
    print("Syntax error in input! \n {s}".format(**{'s':p}))

def build():
    parser = yacc.yacc()

    return parser

def test(data):
    parser = yacc.yacc(**kwargs)
    result = parser.parse(data)
    print(result)
