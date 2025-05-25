from cool_ast.nodes import *

class TypeEnvironment:
    def __init__(self):
        # class_name -> {'parent': parent_name, 'attributes': {attr: type}, 'methods': {method: (param_types, return_type)}}
        self.classes = {}

    def add_class(self, class_name, parent_name=None):
        if class_name in self.classes:
            raise Exception(f"Class {class_name} already defined.")
        self.classes[class_name] = {
            'parent': parent_name,
            'attributes': {},
            'methods': {}
        }

    def add_attribute(self, class_name, attr_name, attr_type):
        if class_name not in self.classes:
            raise Exception(f"Class {class_name} not defined.")
        self.classes[class_name]['attributes'][attr_name] = attr_type

    def add_method(self, class_name, method_name, param_types, return_type):
        if class_name not in self.classes:
            raise Exception(f"Class {class_name} not defined.")
        self.classes[class_name]['methods'][method_name] = (param_types, return_type)

    def get_parent(self, class_name):
        return self.classes[class_name]['parent']

    def get_attribute_type(self, class_name, attr_name):
        return self.classes[class_name]['attributes'].get(attr_name)

    def get_method_signature(self, class_name, method_name):
        return self.classes[class_name]['methods'].get(method_name)

    def has_class(self, class_name):
        return class_name in self.classes

    def __repr__(self):
        return f"TypeEnvironment(classes={self.classes})"

class TypeError(Exception):
    pass

class TypeChecker:
    def __init__(self, ast_root):
        self.ast = ast_root
        self.class_table = {}
        self.current_class = None
        self.current_method = None
        self.local_vars = {}
        self.errors = []
        # Define basic types and their methods
        self.basic_types = {
            'Object': {'parent': None, 'methods': {
                'abort': ([], 'Object'),
                'type_name': ([], 'String'),
                'copy': ([], 'SELF_TYPE')
            }, 'attributes': {}},
            'IO': {'parent': 'Object', 'methods': {
                'out_string': ([('x', 'String')], 'IO'),
                'out_int': ([('x', 'Int')], 'IO'),
                'in_string': ([], 'String'),
                'in_int': ([], 'Int')
            }, 'attributes': {}},
            'Int': {'parent': 'Object', 'methods': {}, 'attributes': {}},
            'String': {'parent': 'Object', 'methods': {
                'length': ([], 'Int'),
                'concat': ([('s', 'String')], 'String'),
                'substr': ([('i', 'Int'), ('l', 'Int')], 'String')
            }, 'attributes': {}},
            'Bool': {'parent': 'Object', 'methods': {}, 'attributes': {}}
        }
        # Initialize class_table with basic types
        self.class_table.update(self.basic_types)

    def check(self):
        """Type check the entire program."""
        if not self.ast:
            print("Empty AST received")
            self.errors.append("Empty AST")
            return False

        try:
            # Build class hierarchy and collect methods/attributes
            print("Building class table...")
            self.build_class_table()
            print(f"Class table: {self.class_table}")
            
            # Check inheritance graph for cycles
            print("Checking inheritance cycles...")
            if not self.check_inheritance_cycles():
                print(f"Inheritance cycle errors: {self.errors}")
                return False
                
            # Type check each class
            print("Type checking classes...")
            for class_node in self.ast.classes:
                print(f"Checking class {class_node.name}")
                self.current_class = class_node.name
                self.local_vars = {}  # Reset local variables for each class
                
                if not self.check_class(class_node):
                    print(f"Class check failed for {class_node.name}")
                    return False
                    
        except Exception as e:
            print(f"Exception during type checking: {str(e)}")
            self.errors.append(str(e))
            return False
            
        # Check Main class and main method exist
        if 'Main' not in self.class_table:
            self.errors.append("Program is missing Main class")
            return False
            
        main_class = self.class_table['Main']
        if 'main' not in main_class['methods']:
            self.errors.append("Main class is missing main method")
            return False

        return len(self.errors) == 0

    def build_class_table(self):
        """Build class hierarchy table with all methods and attributes."""
        # First pass: collect all classes
        for class_node in self.ast.classes:
            if class_node.name in self.class_table:
                self.errors.append(f"Duplicate class definition: {class_node.name}")
                continue
            
            parent = class_node.parent if class_node.parent else 'Object'
            self.class_table[class_node.name] = {
                'parent': parent,
                'methods': {},
                'attributes': {}
            }

        # Second pass: collect methods and attributes
        for class_node in self.ast.classes:
            for feature in class_node.features:
                if isinstance(feature, Method):
                    self.class_table[class_node.name]['methods'][feature.name] = (
                        [(f.name, f.type) for f in feature.formals],
                        feature.return_type
                    )
                elif isinstance(feature, Attribute):
                    self.class_table[class_node.name]['attributes'][feature.name] = feature.type

    def check_inheritance_cycles(self):
        """Check for cycles in the inheritance graph."""
        def has_cycle(class_name, visited):
            # Object class is always valid with no parent
            if class_name == 'Object':
                return False
                
            if class_name in visited:
                self.errors.append(f"Inheritance cycle detected involving class {class_name}")
                return True
                
            if class_name not in self.class_table:
                self.errors.append(f"Class {class_name} not defined")
                return True
                
            parent = self.class_table[class_name]['parent']
            if parent:
                visited.add(class_name)
                if has_cycle(parent, visited):
                    return True
                visited.remove(class_name)
            
            return False

        for class_name in self.class_table:
            if has_cycle(class_name, set()):
                return False
        return True

    def check_class(self, class_node):
        """Type check a class definition."""
        for feature in class_node.features:
            if isinstance(feature, Method):
                if not self.check_method(feature):
                    return False
            elif isinstance(feature, Attribute):
                if not self.check_attribute(feature):
                    return False
        return True

    def check_method(self, method):
        """Type check a method definition."""
        self.current_method = method
        self.local_vars = {}  # Reset local variables
        # Add formal parameters to local variables
        for formal in method.formals:
            self.local_vars[formal.name] = formal.type
        # Check method body
        body_type = self.get_expr_type(method.body)
        declared_type = method.return_type
        # Allow SELF_TYPE to match current class
        if declared_type == 'SELF_TYPE' and (body_type == self.current_class or body_type == 'SELF_TYPE'):
            return True
        if not self.is_subtype(body_type, declared_type):
            self.errors.append(
                f"Method {method.name} in class {self.current_class} has body of type {body_type} "
                f"but declares return type {declared_type}"
            )
            return False
        return True

    def check_attribute(self, attr):
        """Type check an attribute definition."""
        if attr.init:
            init_type = self.get_expr_type(attr.init)
            if not self.is_subtype(init_type, attr.type):
                self.errors.append(
                    f"Attribute {attr.name} initialization has type {init_type} "
                    f"but declares type {attr.type}"
                )
                return False
        return True

    def get_expr_type(self, expr):
        print(f"Type checking expr: {expr} ({type(expr)})")
        """Get the type of an expression."""
        if isinstance(expr, IntegerConstant):
            return 'Int'
        elif isinstance(expr, StringConstant):
            return 'String'
        elif isinstance(expr, BooleanConstant):
            return 'Bool'
        elif isinstance(expr, Identifier):
            if expr.name in self.local_vars:
                return self.local_vars[expr.name]
            if expr.name in self.class_table[self.current_class]['attributes']:
                return self.class_table[self.current_class]['attributes'][expr.name]
            self.errors.append(f"Undefined identifier {expr.name}")
            return 'Object'
        elif isinstance(expr, BinaryOp):
            print(f"Type checking binary op: {expr.op} left={expr.left} right={expr.right}")
            return self.check_binary_op(expr)
        elif isinstance(expr, Dispatch):
            return self.check_dispatch(expr)
        elif isinstance(expr, Conditional):
            return self.check_conditional(expr)
        elif isinstance(expr, Let):
            return self.check_let(expr)
        elif isinstance(expr, New):
            if expr.type not in self.class_table and expr.type != 'SELF_TYPE':
                self.errors.append(f"Cannot instantiate undefined class {expr.type}")
                return 'Object'
            return expr.type
        elif isinstance(expr, IsVoid):
            self.get_expr_type(expr.expr)  # Check the expression
            return 'Bool'
        elif isinstance(expr, Block):
            # Type of a block is the type of its last expression
            for e in expr.expressions[:-1]:
                self.get_expr_type(e)
            return self.get_expr_type(expr.expressions[-1])
        elif isinstance(expr, Case):
            return self.check_case(expr)
        elif isinstance(expr, Self):
            return 'SELF_TYPE'
            
        self.errors.append(f"Unknown expression type: {type(expr)}")
        return 'Object'

    def check_binary_op(self, expr):
        """Type check a binary operation."""
        left_type = self.get_expr_type(expr.left)
        right_type = self.get_expr_type(expr.right)
        
        if expr.op in ['+', '-', '*', '/']:
            if left_type != 'Int' or right_type != 'Int':
                self.errors.append(f"Arithmetic operation requires Int operands")
                return 'Object'
            return 'Int'
        elif expr.op in ['<', '<=']:
            if left_type != 'Int' or right_type != 'Int':
                self.errors.append(f"Comparison operation requires Int operands")
                return 'Object'
            return 'Bool'
        elif expr.op == '=':
            if not self.is_subtype(left_type, right_type) and not self.is_subtype(right_type, left_type):
                self.errors.append(f"Cannot compare expressions of types {left_type} and {right_type}")
                return 'Object'
            return 'Bool'
            
        self.errors.append(f"Unknown binary operator: {expr.op}")
        return 'Object'

    def check_dispatch(self, expr):
        """Type check a method dispatch."""
        # Get type of object being dispatched on
        obj_type = self.current_class if not expr.obj else self.get_expr_type(expr.obj)
        if obj_type == 'SELF_TYPE':
            obj_type = self.current_class
            
        # Find method in class hierarchy
        current = obj_type
        while current:
            if current not in self.class_table:
                self.errors.append(f"Unknown class {current}")
                return 'Object'
                
            methods = self.class_table[current]['methods']
            if expr.method in methods:
                param_types, return_type = methods[expr.method]
                
                # Check number of arguments
                if len(param_types) != len(expr.args):
                    self.errors.append(
                        f"Method {expr.method} expects {len(param_types)} arguments "
                        f"but got {len(expr.args)}"
                    )
                    return 'Object'
                    
                # Check argument types
                for (_, param_type), arg in zip(param_types, expr.args):
                    arg_type = self.get_expr_type(arg)
                    if not self.is_subtype(arg_type, param_type):
                        self.errors.append(
                            f"In call to {expr.method}, argument of type {arg_type} "
                            f"where {param_type} was expected"
                        )
                        return 'Object'
                        
                return return_type if return_type != 'SELF_TYPE' else obj_type
                
            current = self.class_table[current]['parent']
            
        self.errors.append(f"Method {expr.method} not found in class {obj_type} or its ancestors")
        return 'Object'

    def check_conditional(self, expr):
        """Type check an if-then-else expression."""
        pred_type = self.get_expr_type(expr.predicate)
        if pred_type != 'Bool':
            self.errors.append("If condition must be of type Bool")
            return 'Object'
            
        then_type = self.get_expr_type(expr.then_expr)
        else_type = self.get_expr_type(expr.else_expr)
        
        return self.join_types(then_type, else_type)

    def check_let(self, expr):
        """Type check a let expression."""
        old_vars = self.local_vars.copy()
        for binding in expr.bindings:
            if not (isinstance(binding, tuple) and len(binding) == 3):
                self.errors.append(f"Malformed let binding: {binding}")
                return 'Object'
            name, type_name, init = binding
            if init:
                init_type = self.get_expr_type(init)
                if not self.is_subtype(init_type, type_name):
                    self.errors.append(
                        f"Let initialization of {name} has type {init_type} "
                        f"but declares type {type_name}"
                    )
                    return 'Object'
            self.local_vars[name] = type_name
        body_type = self.get_expr_type(expr.body)
        self.local_vars = old_vars
        return body_type

    def check_case(self, expr):
        """Type check a case expression."""
        self.get_expr_type(expr.expr)  # Check the expression being cased on
        
        # Collect types of all branches
        branch_types = []
        seen_types = set()
        
        for branch in expr.cases:
            if branch.type in seen_types:
                self.errors.append(f"Duplicate branch type {branch.type} in case expression")
                return 'Object'
            seen_types.add(branch.type)
            
            # Add the case variable to scope
            old_vars = self.local_vars.copy()
            self.local_vars[branch.name] = branch.type
            
            branch_types.append(self.get_expr_type(branch.expr))
            self.local_vars = old_vars
            
        # Type of case expression is the least upper bound of all branch types
        result_type = branch_types[0]
        for t in branch_types[1:]:
            result_type = self.join_types(result_type, t)
            
        return result_type

    def is_subtype(self, sub_type, super_type):
        """Check if sub_type is a subtype of super_type."""
        if sub_type == 'SELF_TYPE' and super_type == 'SELF_TYPE':
            return True
        if sub_type == 'SELF_TYPE':
            sub_type = self.current_class
        if super_type == 'SELF_TYPE':
            super_type = self.current_class
        current = sub_type
        while current:
            if current == super_type:
                return True
            if current not in self.class_table:
                return False
            current = self.class_table[current]['parent']
        return False

    def join_types(self, type1, type2):
        """Find the least upper bound of two types."""
        if type1 == type2:
            return type1
            
        # Convert SELF_TYPE to actual class name
        if type1 == 'SELF_TYPE':
            type1 = self.current_class
        if type2 == 'SELF_TYPE':
            type2 = self.current_class
            
        # Get all ancestors of type1
        ancestors1 = []
        current = type1
        while current:
            ancestors1.append(current)
            if current not in self.class_table:
                break
            current = self.class_table[current]['parent']
            
        # Walk up type2's ancestor chain until we find a common ancestor
        current = type2
        while current:
            if current in ancestors1:
                return current
            if current not in self.class_table:
                break
            current = self.class_table[current]['parent']
            
        return 'Object'  # Default to Object if no common ancestor found
