class ASTNode:
    def __init__(self):
        self.line = 0
        self.column = 0

class Program(ASTNode):
    def __init__(self, classes):
        super().__init__()
        self.classes = classes

    def __str__(self):
        return f"Program([{', '.join(str(cls) for cls in self.classes)}])"

class Class(ASTNode):
    def __init__(self, name, parent, features):
        super().__init__()
        self.name = name
        self.parent = parent
        self.features = list(features) if features else []

    def __str__(self):
        features_str = ', '.join(str(f) for f in self.features)
        return f"Class({self.name}, {self.parent}, [{features_str}])"

class Method(ASTNode):
    def __init__(self, name, formals, return_type, body):
        super().__init__()
        self.name = name
        self.formals = formals
        self.return_type = return_type
        self.body = body

    @property
    def params(self):
        # Return list of (name, type) tuples as expected by evaluator
        return [(formal.name, formal.type) for formal in self.formals]

    @property
    def expr(self):
        # For compatibility with evaluator
        return self.body

    def __str__(self):
        return f"Method({self.name}, {self.formals}, {self.return_type}, {self.body})"

class Attribute(ASTNode):
    def __init__(self, name, type, init=None):
        super().__init__()
        self.name = name
        self.type = type
        self.init = init

    @property
    def attr_type(self):  # For compatibility with tests
        return self.type

    def __str__(self):
        return f"Attribute({self.name}, {self.type}, {self.init})"

class Formal(ASTNode):
    def __init__(self, name, type):
        super().__init__()
        self.name = name
        self.type = type

    def __str__(self):
        return f"Formal({self.name}, {self.type})"

class IntegerConstant(ASTNode):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def __str__(self):
        return f"Int({self.value})"

class StringConstant(ASTNode):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def __str__(self):
        return f'String("{self.value}")'

class BooleanConstant(ASTNode):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def __str__(self):
        return f"Bool({self.value})"

class Identifier(ASTNode):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def __str__(self):
        return f"Id({self.name})"

class Assign(ASTNode):
    def __init__(self, name, expr):
        super().__init__()
        self.name = name
        self.expr = expr

    def __str__(self):
        return f"Assign({self.name}, {self.expr})"

class Dispatch(ASTNode):
    def __init__(self, obj, method, args):
        super().__init__()
        self.obj = obj
        self.method = method
        self.args = args

    def __getitem__(self, index):
        if index == 0:
            return "dispatch"
        elif index == 1:
            return self.obj
        elif index == 2:
            return self.method
        elif index == 3:
            return self.args
        raise IndexError("Dispatch index out of range")

    def __str__(self):
        obj_str = str(self.obj) if self.obj else "self"
        args_str = ', '.join(str(arg) for arg in self.args)
        return f"{obj_str}.{self.method}({args_str})"

class StaticDispatch(ASTNode):
    def __init__(self, obj, type, method, args):
        super().__init__()
        self.obj = obj
        self.type = type
        self.method = method
        self.args = args

    def __str__(self):
        return f"StaticDispatch({self.obj}, {self.type}, {self.method}, [{', '.join(str(arg) for arg in self.args)}])"

class Conditional(ASTNode):
    def __init__(self, predicate, then_expr, else_expr):
        super().__init__()
        self.predicate = predicate
        self.then_expr = then_expr
        self.else_expr = else_expr

    def __getitem__(self, index):
        if index == 0:
            return "if"
        elif index == 1:
            return self.predicate
        elif index == 2:
            return self.then_expr
        elif index == 3:
            return self.else_expr
        raise IndexError("Conditional index out of range")

    def __str__(self):
        return f"If({self.predicate}, {self.then_expr}, {self.else_expr})"

class Let(ASTNode):
    def __init__(self, bindings, body):
        super().__init__()
        self.bindings = []
        # Convert bindings from various formats to a consistent format
        for binding in bindings:
            if isinstance(binding, tuple):
                if len(binding) == 2:  # (name, type)
                    name, type_ = binding
                    init = None
                elif len(binding) == 3:  # (name, type, init)
                    name, type_, init = binding
                else:
                    raise ValueError(f"Invalid binding format: {binding}")
            elif isinstance(binding, LetBinding):
                name = binding.name
                type_ = binding.type
                init = binding.init
            else:
                raise ValueError(f"Invalid binding format: {binding}")
            self.bindings.append((name, type_, init))  # Keep as tuples for compatibility
        self.body = body

    def __getitem__(self, index):
        if index == 0:
            return "let"
        elif index == 1:
            return self.bindings
        elif index == 2:
            return self.body
        raise IndexError("Let index out of range")

    def __str__(self):
        bindings_str = ', '.join(str(b) for b in self.bindings)
        return f"Let([{bindings_str}], {self.body})"

class LetBinding(ASTNode):
    def __init__(self, name, type_, init=None):
        super().__init__()
        self.name = name
        self.type = type_
        self.init = init

    def __str__(self):
        init_str = f" <- {self.init}" if self.init else ""
        return f"{self.name}: {self.type}{init_str}"

class Block(ASTNode):
    def __init__(self, expressions):
        super().__init__()
        self.expressions = list(expressions) if expressions else []

    def __getitem__(self, index):
        if index == 0:
            return "block"
        elif index == 1:
            return self.expressions
        raise IndexError("Block index out of range")

    def __str__(self):
        expr_str = ', '.join(str(expr) for expr in self.expressions)
        return f"Block([{expr_str}])"

class Case(ASTNode):
    def __init__(self, expr, cases):
        super().__init__()
        self.expr = expr
        self.cases = cases

    def __str__(self):
        return f"Case({self.expr}, [{', '.join(str(c) for c in self.cases)}])"

class Branch(ASTNode):
    def __init__(self, name, type, expr):
        super().__init__()
        self.name = name
        self.type = type
        self.expr = expr

    def __str__(self):
        return f"Branch({self.name}, {self.type}, {self.expr})"

class New(ASTNode):
    def __init__(self, type):
        super().__init__()
        self.type = type

    def __str__(self):
        return f"New({self.type})"

class Not(ASTNode):
    def __init__(self, expr):
        super().__init__()
        self.expr = expr

    def __str__(self):
        return f"Not({self.expr})"

class Negate(ASTNode):
    def __init__(self, expr):
        super().__init__()
        self.expr = expr

    def __str__(self):
        return f"Negate({self.expr})"

class IsVoid(ASTNode):
    def __init__(self, expr):
        super().__init__()
        self.expr = expr

    def __str__(self):
        return f"IsVoid({self.expr})"

class BinaryOp(ASTNode):
    def __init__(self, operator, left, right):
        super().__init__()
        self.operator = operator
        self.left = left
        self.right = right

    def __str__(self):
        return f"BinaryOp({self.operator}, {self.left}, {self.right})"

class Self(ASTNode):
    def __init__(self):
        super().__init__()

    def __str__(self):
        return "self"

class Loop(ASTNode):
    def __init__(self, condition, body):
        super().__init__()
        self.condition = condition
        self.body = body

    def __str__(self):
        return f"Loop({self.condition}, {self.body})"