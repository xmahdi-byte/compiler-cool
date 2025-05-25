from lexer.lexer import lexer
from parser.parser import parser, Class, Method, Attribute

def test_basic_class():
    code = """
    class Main {
        main(): Int { 42 };
    };
    """
    ast = parser.parse(code, lexer=lexer)
    assert len(ast.classes) == 1
    assert ast.classes[0].name == "Main"
    assert len(ast.classes[0].features) == 1
    assert isinstance(ast.classes[0].features[0], Method)
    assert ast.classes[0].features[0].name == "main"
    assert ast.classes[0].features[0].return_type == "Int"

def test_class_inheritance():
    code = """
    class A { };
    class B inherits A { };
    class Main { 
        main(): Int { 42 };
    };
    """
    ast = parser.parse(code, lexer=lexer)
    assert len(ast.classes) == 3
    assert ast.classes[0].name == "A"
    assert ast.classes[1].name == "B"
    assert ast.classes[1].parent == "A"
    assert ast.classes[2].name == "Main"

def test_attributes_and_methods():
    code = """
    class Counter {
        count: Int <- 0;
        increment(): Int {
            count <- count + 1
        };
        get_count(): Int { count };
    };
    """
    ast = parser.parse(code, lexer=lexer)
    assert len(ast.classes) == 1
    features = ast.classes[0].features
    assert len(features) == 3
    assert isinstance(features[0], Attribute)
    assert features[0].name == "count"
    assert features[0].attr_type == "Int"
    assert isinstance(features[1], Method)
    assert features[1].name == "increment"
    assert isinstance(features[2], Method)
    assert features[2].name == "get_count"

def test_control_structures():
    code = """
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
    """
    ast = parser.parse(code, lexer=lexer)
    assert len(ast.classes) == 1
    main_method = ast.classes[0].features[0]
    assert isinstance(main_method, Method)
    assert main_method.name == "main"
    # The expression tree should contain if and while expressions
    expr = main_method.expr
    assert expr[0] == "if"  # if expression

def test_let_expressions():
    code = """
    class Main {
        main(): Int {
            let x: Int <- 5,
                y: Int <- 10
            in x + y
        };
    };
    """
    ast = parser.parse(code, lexer=lexer)
    assert len(ast.classes) == 1
    main_method = ast.classes[0].features[0]
    expr = main_method.expr
    assert expr[0] == "let"  # let expression
    bindings = expr[1]
    assert len(bindings) == 2  # Two bindings

def test_method_calls():
    code = """
    class Main {
        foo(): Int { 42 };
        main(): Int {
            self.foo()
        };
    };
    """
    ast = parser.parse(code, lexer=lexer)
    assert len(ast.classes) == 1
    assert len(ast.classes[0].features) == 2
    main_method = ast.classes[0].features[1]
    expr = main_method.expr
    assert expr[0] == "dispatch"  # Method call expression

def test_complex_expressions():
    code = """
    class Main {
        main(): Int {
            let x: Int <- 5 in {
                if x < 10 then
                    x <- x + 1
                else
                    x <- x - 1
                fi;
                x * 2
            }
        };
    };
    """
    ast = parser.parse(code, lexer=lexer)
    assert len(ast.classes) == 1
    main_method = ast.classes[0].features[0]
    expr = main_method.expr
    assert expr[0] == "let"  # let expression
    block_expr = expr[2]
    assert block_expr[0] == "block"  # Block expression
