from lexer.lexer import lexer
from parser.parser import parser
from interpreter.evaluator import Evaluator

def test_simple_arithmetic():
    code = """
    class Main {
        main(): Int {
            2 + 3 * 4
        };
    };
    """
    lexer.input(code)
    ast_root = parser.parse(code, lexer=lexer)
    evaluator = Evaluator(ast_root)
    assert evaluator.eval() == 14

def test_if_else():
    code = """
    class Main {
        main(): Int {
            if 1 < 2 then 10 else 20 fi
        };
    };
    """
    lexer.input(code)
    ast_root = parser.parse(code, lexer=lexer)
    evaluator = Evaluator(ast_root)
    assert evaluator.eval() == 10

def test_let_binding():
    code = """
    class Main {
        main(): Int {
            let x: Int <- 7 in x * 2
        };
    };
    """
    lexer.input(code)
    ast_root = parser.parse(code, lexer=lexer)
    evaluator = Evaluator(ast_root)
    assert evaluator.eval() == 14

def test_method_call():
    code = """
    class Main {
        main(): Int {
            self.foo()
        };
        foo(): Int { 42 };
    };
    """
    lexer.input(code)
    ast_root = parser.parse(code, lexer=lexer)
    evaluator = Evaluator(ast_root)
    assert evaluator.eval() == 42

def test_object_creation_and_attr():
    code = """
    class A {
        x: Int <- 5;
        get_x(): Int { x };
    };
    class Main {
        main(): Int {
            (new A).get_x()
        };
    };
    """
    lexer.input(code)
    ast_root = parser.parse(code, lexer=lexer)
    evaluator = Evaluator(ast_root)
    assert evaluator.eval() == 5

def test_while_loop():
    code = """
    class Main {
        main(): Int {
            let x: Int <- 0 in {
                while x < 3 loop x <- x + 1 pool;
                x;
            }
        };
    };
    """
    lexer.input(code)
    ast_root = parser.parse(code, lexer=lexer)
    evaluator = Evaluator(ast_root)
    result = evaluator.eval()
    assert result == 3

def test_case_expression():
    code = """
    class A { };
    class B inherits A { };
    class Main {
        main(): Int {
            case new B of
                a: A => 1;
                b: B => 2;
            esac
        };
    };
    """
    lexer.input(code)
    ast_root = parser.parse(code, lexer=lexer)
    evaluator = Evaluator(ast_root)
    assert evaluator.eval() == 2

if __name__ == "__main__":
    test_simple_arithmetic()
    test_if_else()
    test_let_binding()
    test_method_call()
    test_object_creation_and_attr()
    test_while_loop()
    test_case_expression()
    print("All operational semantics tests passed.")
