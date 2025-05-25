class Environment:
    def __init__(self, parent=None):
        self.vars = {}
        self.parent = parent

    def get(self, name):
        if name in self.vars:
            return self.vars[name]
        elif self.parent:
            return self.parent.get(name)
        else:
            raise RuntimeError(f"Undefined variable {name}")

    def set(self, name, value):
        if name in self.vars:
            self.vars[name] = value
        elif self.parent:
            self.parent.set(name, value)
        else:
            self.vars[name] = value

class COOLObject:
    def __init__(self, class_name, class_defs):
        self.__class_name__ = class_name
        self.__class_defs__ = class_defs
        self.__attrs__ = {}
        # Initialize attributes from class and ancestors
        self._init_attrs(class_name)

    def _init_attrs(self, class_name):
        class_def = self.__class_defs__[class_name]
        # First initialize parent's attributes
        if hasattr(class_def, 'parent') and class_def.parent:
            self._init_attrs(class_def.parent)
        # Then add/override attributes from this class
        for feat in getattr(class_def, 'features', []):
            if hasattr(feat, 'name') and hasattr(feat, 'type'):
                # Get initialization expression if any
                init = feat.init if hasattr(feat, 'init') else None
                # Initialize with None - will be evaluated in New expression
                self.__attrs__[feat.name] = init

    def get_attr(self, name):
        if name in self.__attrs__:
            return self.__attrs__[name]
        raise RuntimeError(f"Attribute {name} not found in object of class {self.__class_name__}")

    def set_attr(self, name, value):
        if name in self.__attrs__:
            self.__attrs__[name] = value
        else:
            raise RuntimeError(f"Attribute {name} not found in object of class {self.__class_name__}")

    def get_class(self):
        return self.__class_defs__[self.__class_name__]

    def get_ancestors(self):
        # Returns list of class names from self up to Object
        names = []
        c = self.__class_name__
        while c:
            names.append(c)
            cdef = self.__class_defs__[c]
            c = getattr(cdef, 'parent', None)
        return names

class Evaluator:
    def __init__(self, ast_root):
        self.ast = ast_root
        self.global_env = Environment()
        # Collect all classes from the AST, including nested classes
        self.class_defs = {}
        def collect_classes(classes):
            for cls in classes:
                self.class_defs[cls.name] = cls
        if hasattr(ast_root, 'classes'):
            collect_classes(ast_root.classes)

    def eval(self):
        # Entry point: look for Main class and main method
        main_class = self.class_defs.get('Main')
        if not main_class:
            raise RuntimeError("No Main class found")

        main_method = None
        for f in main_class.features:
            if hasattr(f, 'name') and f.name == 'main':
                main_method = f
                break

        if not main_method:
            raise RuntimeError("No main method found in Main class")

        # Instantiate Main object and set 'self' in env
        main_obj = COOLObject('Main', self.class_defs)
        env = Environment(self.global_env)
        env.set('self', main_obj)
        return self.eval_method(main_method, [], env)

    def eval_method(self, method, args, env=None):
        if env is None:
            env = Environment(self.global_env)
        # 'self' should already be set in env if provided
        for (name, _), val in zip(method.params, args):
            env.set(name, val)
        return self.eval_expr(method.expr, env)

    def eval_expr(self, expr, env):
        # Support for custom AST node classes
        from cool_ast.nodes import IntegerConstant, BooleanConstant, StringConstant
        from cool_ast.nodes import BinaryOp, UnaryOp, Identifier, Conditional
        from cool_ast.nodes import Let, Dispatch, New, Loop, Case, Block, Branch, Assign, Self

        if isinstance(expr, int) or isinstance(expr, bool):
            return expr
        elif isinstance(expr, IntegerConstant):
            return expr.value
        elif isinstance(expr, BooleanConstant):
            return expr.value
        elif isinstance(expr, StringConstant):
            return expr.value
        elif isinstance(expr, Self):
            return env.get('self')
        elif isinstance(expr, Identifier):
            # For identifiers, first check if it's an attribute of self
            if 'self' in env.vars and isinstance(env.get('self'), COOLObject):
                self_obj = env.get('self')
                if expr.name in self_obj.__attrs__:
                    return self_obj.get_attr(expr.name)
            # Then try to get from current environment
            try:
                return env.get(expr.name)
            except RuntimeError:
                raise RuntimeError(f"Undefined variable or attribute {expr.name}")

        elif isinstance(expr, BinaryOp):
            lval = self.eval_expr(expr.left, env)
            rval = self.eval_expr(expr.right, env)
            if expr.op == '+': return lval + rval
            if expr.op == '-': return lval - rval
            if expr.op == '*': return lval * rval
            if expr.op == '/': return lval // rval
            if expr.op == '<': return lval < rval
            if expr.op == '<=': return lval <= rval
            if expr.op == '=': return lval == rval
            raise RuntimeError(f"Unknown operator {expr.op}")
        elif isinstance(expr, UnaryOp):
            val = self.eval_expr(expr.expr, env)
            if expr.op == 'not': return not val
            if expr.op == 'negate': return -val
            raise RuntimeError(f"Unknown unary operator {expr.op}")
        elif isinstance(expr, Conditional):
            condition = self.eval_expr(expr.predicate, env)
            if condition:
                return self.eval_expr(expr.then_expr, env)
            else:
                return self.eval_expr(expr.else_expr, env)
        elif isinstance(expr, Let):
            let_env = Environment(env)
            # bindings should be list of (name, type, init) tuples
            for name, _, init in expr.bindings:
                value = self.eval_expr(init, let_env) if init else None
                let_env.set(name, value)
            return self.eval_expr(expr.body, let_env)
        elif isinstance(expr, Dispatch):
            obj = self.eval_expr(expr.obj, env) if expr.obj else env.get('self')
            if not isinstance(obj, COOLObject):
                raise RuntimeError('Dispatch on non-object')
            # Find method in class hierarchy
            method = self._find_method(obj.get_class(), expr.method)
            if not method:
                raise RuntimeError(f"Method {expr.method} not found in class {obj.__class_name__}")
            # Create new environment for method
            method_env = Environment()
            method_env.set('self', obj)
            # Evaluate arguments and bind them to parameters
            arg_vals = [self.eval_expr(arg, env) for arg in expr.args]
            for (name, _), val in zip(method.params, arg_vals):
                method_env.set(name, val)
            return self.eval_expr(method.expr, method_env)
        elif isinstance(expr, New):
            class_name = expr.type
            if class_name not in self.class_defs:
                raise RuntimeError(f"Class {class_name} not found")
            obj = COOLObject(class_name, self.class_defs)
            # Create a new environment for evaluating initializers with self set to obj
            init_env = Environment()
            init_env.set('self', obj)
            # Evaluate attribute initializers in new environment
            for attr_name, init_expr in obj.__attrs__.items():
                if init_expr is not None:
                    obj.__attrs__[attr_name] = self.eval_expr(init_expr, init_env)
            return obj
        elif isinstance(expr, Loop):
            while self.eval_expr(expr.condition, env):
                self.eval_expr(expr.body, env)
            return None
        elif isinstance(expr, Block):
            value = None
            for exp in expr.expressions:
                value = self.eval_expr(exp, env)
            return value
        elif isinstance(expr, Case):
            val = self.eval_expr(expr.expr, env)
            if not isinstance(val, COOLObject):
                raise RuntimeError('Case on non-object')
            val_types = val.get_ancestors()
            # For each type in ancestor list (most specific first)
            for current_type in val_types:
                # Find first branch matching this type
                for case_branch in expr.cases:
                    if case_branch.type == current_type:
                        case_env = Environment(env)
                        case_env.set(case_branch.name, val)
                        return self.eval_expr(case_branch.expr, case_env)
            raise RuntimeError('No matching branch in case')
        elif isinstance(expr, Assign):
            value = self.eval_expr(expr.expr, env)
            # Check if assigning to attribute of self
            if expr.name != 'self' and 'self' in env.vars and isinstance(env.get('self'), COOLObject):
                self_obj = env.get('self')
                if expr.name in self_obj.__attrs__:
                    self_obj.set_attr(expr.name, value)
                    return value
            # Otherwise set in current environment
            env.set(expr.name, value)
            return value
        elif isinstance(expr, str):
            try:
                return env.get(expr)
            except RuntimeError:
                # If not found in env, check if it's an attribute of self
                if 'self' in env.vars and isinstance(env.get('self'), COOLObject):
                    self_obj = env.get('self')
                    if expr in self_obj.__attrs__:
                        return self_obj.get_attr(expr)
            raise
        else:
            raise RuntimeError(f"Unsupported expression type {expr}")

    def _instantiate(self, class_name):
        # Create a new object instance, set attributes (with inheritance)
        class_def = self.class_defs.get(class_name)
        if not class_def:
            raise RuntimeError(f"Class {class_name} not found")
        # Build attribute dict with inheritance
        attrs = {}
        def collect_attrs(cls):
            if cls.parent:
                parent_cls = self.class_defs.get(cls.parent)
                if parent_cls:
                    collect_attrs(parent_cls)
            for feat in cls.features:
                if hasattr(feat, 'name') and hasattr(feat, 'attr_type'):
                    attrs[feat.name] = None
        collect_attrs(class_def)
        # Create object
        obj = type('COOLObject', (), {})()
        obj.__class_name__ = class_name
        for name in attrs:
            setattr(obj, name, None)
        # Initialize attributes
        for feat in class_def.features:
            if hasattr(feat, 'name') and hasattr(feat, 'attr_type'):
                val = feat.init_expr if hasattr(feat, 'init_expr') else None
                setattr(obj, feat.name, self.eval_expr(val, Environment()) if val is not None else None)
        return obj

    def _dispatch(self, obj, method_name, args, env, static_type=None):
        # Find method in class or its ancestors
        class_name = static_type if static_type else getattr(obj, '__class_name__', None)
        cls = self.class_defs.get(class_name)
        while cls:
            for f in cls.features:
                if hasattr(f, 'name') and hasattr(f, 'attr_type') and f.name == method_name:
                    method = f
                    method_env = Environment()
                    method_env.set('self', obj)
                    for (name, _), val in zip(method.params, [self.eval_expr(a, env) for a in args]):
                        method_env.set(name, val)
                    return self.eval_expr(method.expr, method_env)
            if cls.parent:
                cls = self.class_defs.get(cls.parent)
            else:
                break
        raise RuntimeError(f"Method {method_name} not found in class hierarchy of {class_name}")

    def _find_method(self, class_def, method_name):
        # Traverse inheritance chain to find method
        cdef = class_def
        while cdef:
            for f in getattr(cdef, 'features', []):
                if hasattr(f, 'name') and f.name == method_name:
                    return f
            cdef = self.class_defs.get(getattr(cdef, 'parent', None))
        return None
