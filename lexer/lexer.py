import ply.lex as lex


# Reserved keywords
reserved = {
    'class': 'CLASS',
    'inherits': 'INHERITS',
    'if': 'IF',
    'then': 'THEN',
    'else': 'ELSE',
    'fi': 'FI',
    'while': 'WHILE',
    'loop': 'LOOP',
    'pool': 'POOL',
    'let': 'LET',
    'in': 'IN',
    'case': 'CASE',
    'of': 'OF',
    'esac': 'ESAC',
    'new': 'NEW',
    'isvoid': 'ISVOID',
    'not': 'NOT'
}

# List of token names
tokens = [
    'TYPEID', 'OBJECTID',
    'INT_CONST', 'STR_CONST',
    'BOOL_CONST',  # For true/false literals
    'ASSIGN', 'DARROW',
    'PLUS', 'MINUS', 'MULT', 'DIV',
    'LT', 'LE', 'EQ',
    'LPAREN', 'RPAREN',
    'LBRACE', 'RBRACE',
    'SEMI', 'COLON', 'COMMA', 'DOT',
    'AT', 'AND', 'OR'
] + list(reserved.values())

states = (
    ('blockcomment', 'exclusive'),
)

# Regular expressions for simple tokens
t_ASSIGN = r'<-'
t_DARROW = r'=>'
t_PLUS   = r'\+'
t_MINUS  = r'-'
t_MULT   = r'\*'
t_DIV    = r'/'
t_LT     = r'<'
t_LE     = r'<='
t_EQ     = r'='
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_SEMI   = r';'
t_COLON  = r':'
t_COMMA  = r','
t_DOT    = r'\.'
t_AT     = r'@'
t_AND    = r'&&'
t_OR     = r'\|\|'

# Whitespace and comments
t_ignore = ' \t\r'
t_ignore_COMMENT = r'--.*'

def t_blockcomment(t):
    r'\(\*'
    t.lexer.push_state('blockcomment')
    t.lexer.block_comment_level = getattr(t.lexer, 'block_comment_level', 0) + 1

def t_blockcomment_end(t):
    r'\*\)'
    t.lexer.block_comment_level -= 1
    if t.lexer.block_comment_level == 0:
        t.lexer.pop_state()

def t_blockcomment_newstart(t):
    r'\(\*'
    t.lexer.block_comment_level += 1

def t_blockcomment_content(t):
    r'[^(*]+|[(*]'
    pass

t_blockcomment_ignore = ' \t\r\n'

def t_blockcomment_error(t):
    t.lexer.skip(1)

def t_TYPEID(t):
    r'[A-Z][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value.lower(), 'TYPEID')
    return t

def t_BOOL_CONST(t):
    r'(?i:true|false)'
    t.value = t.value.lower() == 'true'
    t.type = 'BOOL_CONST'
    return t

def t_OBJECTID(t):
    r'[a-z][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value.lower(), 'OBJECTID')
    return t


def t_INT_CONST(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_STR_CONST(t):
    r'"([^\\"]|\\.)*"'
    t.value = t.value[1:-1]  # remove the quotes
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print(f"Illegal character '{t.value[0]}' at line {t.lineno}")
    t.lexer.skip(1)

# Build the lexer
def get_lexer():
    return lex.lex()

# Create and export a lexer instance
lexer = get_lexer()

