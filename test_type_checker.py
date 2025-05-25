import pytest
from parser.parser import parser
from lexer.lexer import lexer
from semantics.type_environment import TypeChecker


class TestTypeChecker:
    def check_program(self, code: str) -> bool:
        """Helper method to run type checking on COOL code."""
        try:
            lexer.input(code)
            ast_root = parser.parse(code, lexer=lexer)
            type_checker = TypeChecker(ast_root)
            return type_checker.check()
        except Exception as e:
            print(f"Error: {str(e)}")
            return False

    def test_basic_types(self):
        """Test basic type checking for primitive types."""
        code = '''
        class Main {
            x : Int <- 42;
            y : String <- "hello";
            b : Bool <- true;
            main() : Int { x };
        };
        '''
        assert self.check_program(code)

    def test_type_inheritance(self):
        """Test type checking with inheritance."""
        code = '''
        class A {
            foo() : Int { 1 };
        };
        class B inherits A {
            bar() : Int { foo() };
        };
        class Main {
            a : A <- new A;
            b : B <- new B;
            main() : A { b };
        };
        '''
        assert self.check_program(code)

    def test_method_types(self):
        """Test method type checking."""
        code = '''
        class Main {
            foo() : Int { 42 };
            bar(x : Int) : String { "hello" };
            baz(s : String) : Int { foo() };
            main() : String { bar(baz("test")) };
        };
        '''
        assert self.check_program(code)

    def test_arithmetic_types(self):
        """Test arithmetic expressions."""
        code = '''
        class Main {
            main() : Int { 
                let x : Int <- 5,
                    y : Int <- 3
                in x + y * 2 - (4 / 2)
            };
        };
        '''
        assert self.check_program(code)

    def test_comparison_types(self):
        """Test comparison expressions."""
        code = '''
        class Main {
            main() : Bool {
                let x : Int <- 5,
                    y : Int <- 3
                in (x <= y) 
            };
        };
        '''
        assert self.check_program(code)

    def test_if_condition_types(self):
        """Test if-then-else expressions."""
        code = '''
        class Main {
            main() : Object {
                if 1 < 2 then
                    "true branch"
                else
                    42
                fi
            };
        };
        '''
        assert self.check_program(code)

    def test_case_types(self):
        """Test case expressions."""
        code = '''
        class A {};
        class B inherits A {};
        class C inherits B {};
        class Main {
            main() : Int {
                case new C of
                    a : A => 1;
                    b : B => 2;
                    c : C => 3;
                esac
            };
        };
        '''
        assert self.check_program(code)

    def test_let_binding_types(self):
        """Test let expressions."""
        code = '''
        class Main {
            main() : Int {
                let x : Int <- 5,
                    y : String <- "hello",
                    z : Int,
                    b : Bool <- true
                in 
                    if b then x + 1 else z fi
            };
        };
        '''
        assert self.check_program(code)

    def test_dispatch_types(self):
        """Test method dispatch."""
        code = '''
        class A {
            foo(x : Int) : Int { x + 1 };
            bar(s : String) : String { s };
        };
        class B inherits A {
            baz(x : Int, s : String) : String { bar(s) };
        };
        class Main {
            a : A <- new A;
            b : B <- new B;
            main() : String {
                b.baz(a.foo(42), "test")
            };
        };
        '''
        assert self.check_program(code)

    def test_self_type(self):
        """Test SELF_TYPE."""
        code = '''
        class Main {
            copy() : SELF_TYPE { self };
            main() : SELF_TYPE { copy() };
        };
        '''
        assert self.check_program(code)


if __name__ == "__main__":
    pytest.main()
