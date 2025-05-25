import ply.yacc as yacc
from lexer.lexer import tokens  # import tokens list from lexer.py
from cool_ast.nodes import *

# Precedence rules for operators
precedence = (
    ('right', 'ASSIGN'),
    ('left', 'NOT'),
    ('nonassoc', 'LE', 'LT', 'EQ'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'MULT', 'DIV'),
    ('right', 'ISVOID'),
    ('right', 'AT'),
    ('right', 'DOT'),
)

def p_program(p):
    '''program : class_list'''
    p[0] = Program(p[1])

def p_class_list(p):
    '''class_list : class_list class SEMI
                  | class SEMI'''
    if len(p) == 4:
        classes = list(p[1])
        classes.append(p[2])
        p[0] = classes
    else:
        p[0] = [p[1]]

def p_class(p):
    '''class : CLASS TYPEID LBRACE feature_list RBRACE
            | CLASS TYPEID INHERITS TYPEID LBRACE feature_list RBRACE'''
    if len(p) == 6:
        p[0] = Class(p[2], 'Object', p[4])  # Default parent is Object
    else:
        p[0] = Class(p[2], p[4], p[6])

def p_feature_list(p):
    '''feature_list : feature_list feature SEMI
                   | empty'''
    if len(p) == 4:
        features = list(p[1]) if p[1] else []
        features.append(p[2])
        p[0] = features
    else:
        p[0] = []

def p_feature_method(p):
    '''feature : OBJECTID LPAREN formal_list RPAREN COLON TYPEID LBRACE expr RBRACE'''
    p[0] = Method(p[1], p[3], p[6], p[8])

def p_feature_attr(p):
    '''feature : OBJECTID COLON TYPEID ASSIGN expr
               | OBJECTID COLON TYPEID'''
    if len(p) == 6:
        p[0] = Attribute(p[1], p[3], p[5])
    else:
        p[0] = Attribute(p[1], p[3])

def p_formal_list(p):
    '''formal_list : formal_list COMMA formal
                  | formal
                  | empty'''
    if len(p) == 4:
        formals = list(p[1]) if p[1] else []
        formals.append(p[3])
        p[0] = formals
    elif len(p) == 2 and p[1] is not None:
        p[0] = [p[1]]
    else:
        p[0] = []

def p_formal(p):
    '''formal : OBJECTID COLON TYPEID'''
    p[0] = Formal(p[1], p[3])

def p_expr(p):
    '''expr : BOOL_CONST
           | INT_CONST
           | STR_CONST
           | OBJECTID
           | new_expr
           | assign_expr
           | dispatch_expr
           | if_expr
           | while_expr
           | block_expr
           | let_expr
           | case_expr
           | arithmetic_expr
           | comparison_expr
           | paren_expr
           | ISVOID expr
           | NOT expr'''
    if isinstance(p[1], bool):
        p[0] = BooleanConstant(p[1])
    elif isinstance(p[1], int):
        p[0] = IntegerConstant(p[1])
    elif isinstance(p[1], str) and p.slice[1].type == 'STR_CONST':
        p[0] = StringConstant(p[1])
    elif isinstance(p[1], str) and p.slice[1].type == 'OBJECTID':
        p[0] = Identifier(p[1]) if p[1] != 'self' else Self()
    elif p.slice[1].type == 'ISVOID':
        p[0] = IsVoid(p[2])
    elif p.slice[1].type == 'NOT':
        p[0] = Not(p[2])
    else:
        p[0] = p[1]

def p_new_expr(p):
    '''new_expr : NEW TYPEID'''
    p[0] = New(p[2])

def p_assign_expr(p):
    '''assign_expr : OBJECTID ASSIGN expr'''
    p[0] = Assign(p[1], p[3])

def p_dispatch_expr(p):
    '''dispatch_expr : expr DOT OBJECTID LPAREN expr_list RPAREN
                    | expr AT TYPEID DOT OBJECTID LPAREN expr_list RPAREN
                    | OBJECTID LPAREN expr_list RPAREN'''
    if len(p) == 7:
        p[0] = Dispatch(p[1], p[3], p[5])
    elif len(p) == 9:
        p[0] = StaticDispatch(p[1], p[3], p[5], p[7])
    else:
        p[0] = Dispatch(None, p[1], p[3])

def p_if_expr(p):
    '''if_expr : IF expr THEN expr ELSE expr FI'''
    p[0] = Conditional(p[2], p[4], p[6])

def p_while_expr(p):
    '''while_expr : WHILE expr LOOP expr POOL'''
    p[0] = Loop(p[2], p[4])

def p_block_expr(p):
    '''block_expr : LBRACE expr_list_semi RBRACE'''
    # Handle empty block
    if not p[2]:
        p[0] = Block([])
        return
        
    # Filter out None values that might have come from error recovery
    exprs = [expr for expr in p[2] if expr is not None]
    
    # Must have at least one valid expression
    if not exprs:
        p[0] = None  # Parsing error
    else:
        p[0] = Block(exprs)

def p_let_expr(p):
    '''let_expr : LET let_list IN expr'''
    # Ensure bindings is a list
    bindings = p[2] if isinstance(p[2], list) else [p[2]]
    # Filter out None bindings that might have come from error recovery
    bindings = [b for b in bindings if b is not None]
    p[0] = Let(bindings, p[4])

def p_let_list(p):
    '''let_list : let_list COMMA let_binding
                | let_binding'''
    if len(p) == 4:
        bindings = list(p[1]) if isinstance(p[1], list) else [p[1]]
        if p[3] is not None:  # Only add valid bindings
            bindings.append(p[3])
        p[0] = bindings
    else:
        p[0] = [p[1]] if p[1] is not None else []

def p_let_binding(p):
    '''let_binding : OBJECTID COLON TYPEID
                  | OBJECTID COLON TYPEID ASSIGN expr'''
    if len(p) == 4:
        p[0] = LetBinding(p[1], p[3])
    else:
        p[0] = LetBinding(p[1], p[3], p[5])

def p_case_expr(p):
    '''case_expr : CASE expr OF case_list ESAC'''
    p[0] = Case(p[2], p[4])

def p_case_list(p):
    '''case_list : case_list OBJECTID COLON TYPEID DARROW expr SEMI
                | OBJECTID COLON TYPEID DARROW expr SEMI'''
    if len(p) == 8:
        prev = list(p[1]) if isinstance(p[1], list) else [p[1]]
        prev.append(Branch(p[2], p[4], p[6]))
        p[0] = prev
    else:
        p[0] = [Branch(p[1], p[3], p[5])]

def p_expr_list_semi(p):
    '''expr_list_semi : expr_list_semi expr SEMI
                     | expr SEMI'''
    if len(p) == 4:
        exprs = list(p[1]) if p[1] is not None else []
        if p[2] is not None:  # Only add valid expressions
            exprs.append(p[2])
        p[0] = exprs
    else:
        p[0] = [p[1]] if p[1] is not None else []

def p_expr_list(p):
    '''expr_list : expr_list COMMA expr
                | expr
                | empty'''
    if len(p) == 4:  # expr_list COMMA expr
        if p[1] is None or p[3] is None:  # Error in expressions
            p[0] = None
        else:
            exprs = list(p[1])
            exprs.append(p[3])
            p[0] = exprs
    elif len(p) == 2 and p[1] is not None:  # expr
        p[0] = [p[1]]
    else:  # empty
        p[0] = []

def p_arithmetic_expr(p):
    '''arithmetic_expr : expr PLUS expr
                      | expr MINUS expr
                      | expr MULT expr
                      | expr DIV expr
                      | TILDE expr
                      | expr LT expr
                      | expr LE expr
                      | expr EQ expr'''
    if len(p) == 3:  # Unary operator
        if p[1] == '~':
            p[0] = Negate(p[2])
    else:  # Binary operator
        p[0] = BinaryOp(p[2], p[1], p[3])

def p_comparison_expr(p):
    '''comparison_expr : expr LT expr
                      | expr LE expr
                      | expr EQ expr'''
    p[0] = BinaryOp(p[1], p[2], p[3])

def p_paren_expr(p):
    '''paren_expr : LPAREN expr RPAREN'''
    p[0] = p[2]  # Pass through the expression inside parentheses

def p_empty(p):
    'empty :'
    pass

def p_error(p):
    if p:
        raise SyntaxError(f"Syntax error at '{p.value}' line {p.lineno}")
    else:
        raise SyntaxError("Syntax error at EOF")

# Add error recovery rules
def p_error_class(p):
    '''class : CLASS error SEMI'''
    p[0] = None  # Skip class with error

def p_error_feature(p):
    '''feature : error SEMI'''
    p[0] = None  # Skip feature with error

def p_error_expr(p):
    '''expr : error SEMI'''
    p[0] = None  # Skip expression with error

parser = yacc.yacc(debug=False)
