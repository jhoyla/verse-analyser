import ply.yacc as yacc
from manuscriptslex import ManuscriptsLexer
tokens = ManuscriptsLexer.tokens

def p_manuscripts(p):
    '''manuscripts : man_list NEW_LINE'''
    p[0] = p[1]
    

def p_man_list(p):
    '''man_list : MANUSCRIPT
    | MANUSCRIPT COMMA man_list'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]

def p_error(p):
    print("Syntax error in manuscripts input")


def build():
    parser = yacc.yacc()
    return parser


