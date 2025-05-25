from lexer.lexer import lexer

def test_basic_class():
    code = '''
    class Main {
        main(): Int { 42 };
    };
    '''
    lexer.input(code)
    tokens = [tok.type for tok in lexer]
    expected = ['CLASS', 'TYPEID', 'LBRACE', 'OBJECTID', 'LPAREN', 'RPAREN', 
                'COLON', 'TYPEID', 'LBRACE', 'INT_CONST', 'RBRACE', 'SEMI', 'RBRACE', 'SEMI']
    assert tokens == expected, f"Expected {expected}, got {tokens}"

def test_class_with_inheritance():
    code = '''
    class Main inherits IO {
        main(): Int { 42 };
    };
    '''
    lexer.input(code)
    tokens = [tok.type for tok in lexer]
    expected = ['CLASS', 'TYPEID', 'INHERITS', 'TYPEID', 'LBRACE', 'OBJECTID', 
                'LPAREN', 'RPAREN', 'COLON', 'TYPEID', 'LBRACE', 'INT_CONST', 
                'RBRACE', 'SEMI', 'RBRACE', 'SEMI']
    assert tokens == expected, f"Expected {expected}, got {tokens}"

def test_attributes_and_methods():
    code = '''
    class Counter {
        count: Int <- 0;
        increment(): Int {
            count <- count + 1
        };
    };
    '''
    lexer.input(code)
    tokens = [tok.type for tok in lexer]
    expected = ['CLASS', 'TYPEID', 'LBRACE', 'OBJECTID', 'COLON', 'TYPEID', 
                'ASSIGN', 'INT_CONST', 'SEMI', 'OBJECTID', 'LPAREN', 'RPAREN', 
                'COLON', 'TYPEID', 'LBRACE', 'OBJECTID', 'ASSIGN', 'OBJECTID', 
                'PLUS', 'INT_CONST', 'RBRACE', 'SEMI', 'RBRACE', 'SEMI']
    assert tokens == expected, f"Expected {expected}, got {tokens}"

def test_control_structures():
    code = '''
    class Main {
        main(): Int {
            if x < 10 then
                while y < 5 loop
                    y <- y - 1
                pool
            else
                0
            fi
        };
    };
    '''
    lexer.input(code)
    tokens = [tok.type for tok in lexer]
    expected = ['CLASS', 'TYPEID', 'LBRACE', 'OBJECTID', 'LPAREN', 'RPAREN', 
                'COLON', 'TYPEID', 'LBRACE', 'IF', 'OBJECTID', 'LT', 'INT_CONST', 
                'THEN', 'WHILE', 'OBJECTID', 'LT', 'INT_CONST', 'LOOP', 'OBJECTID', 
                'ASSIGN', 'OBJECTID', 'MINUS', 'INT_CONST', 'POOL', 'ELSE', 'INT_CONST', 
                'FI', 'RBRACE', 'SEMI', 'RBRACE', 'SEMI']
    assert tokens == expected, f"Expected {expected}, got {tokens}"

def test_let_expressions():
    code = '''
    class Main {
        main(): Int {
            let x: Int <- 5,
                y: String <- "hello"
            in x + 1
        };
    };
    '''
    lexer.input(code)
    tokens = [tok.type for tok in lexer]
    expected = ['CLASS', 'TYPEID', 'LBRACE', 'OBJECTID', 'LPAREN', 'RPAREN', 
                'COLON', 'TYPEID', 'LBRACE', 'LET', 'OBJECTID', 'COLON', 'TYPEID', 
                'ASSIGN', 'INT_CONST', 'COMMA', 'OBJECTID', 'COLON', 'TYPEID', 
                'ASSIGN', 'STR_CONST', 'IN', 'OBJECTID', 'PLUS', 'INT_CONST', 
                'RBRACE', 'SEMI', 'RBRACE', 'SEMI']
    assert tokens == expected, f"Expected {expected}, got {tokens}"

if __name__ == "__main__":
    test_basic_class()
    test_class_with_inheritance()
    test_attributes_and_methods()
    test_control_structures()
    test_let_expressions()
    print("All lexer tests passed.")
