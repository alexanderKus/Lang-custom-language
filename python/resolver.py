from common import Visitor
from enum import Enum

class FunctionType(Enum):
    NONE = 1,
    FUNCTION = 2
    METHOD = 3
    INITIALIZER = 4

class ClassType(Enum):
    NONE = 0,
    CLASS = 1

class VariableState(Enum):
    DECLARED = 0,
    DEFINED = 1,
    READ = 3
    CLASS_NAME = 4

class Variable:
    def __init__(self, name, state):
        self.name = name
        self.state = state

class Resolver(Visitor):
    # NOTE: If more static analysis is need, add them here
    # Example 1: add warning about unreachable code after return statement
    def __init__(self, interpreter, eh):
        self.interpreter = interpreter
        self.eh = eh
        self.scopes = []
        self.current_function = FunctionType.NONE
        self.current_class = ClassType.NONE
        self.inside_loop = False

    def resolve(self, stmts):
        for stmt in stmts:
            self._resolve(stmt)
    
    # NOTE: works for expr too
    def _resolve(self, stmt):
        stmt.accept(self)

    def begin_scope(self):
        self.scopes.append({})

    def end_scope(self):
        scope = self.scopes.pop()
        for entry in scope.values():
            if entry.state == VariableState.DEFINED:
                # self.eh.errorT(entry.name, 'Local variable is not used')
                self.eh.warningT(entry.name, 'local variable is not used')
    
    def visit_class_stmt(self, stmt):
        enclosing_class = self.current_class
        self.current_class = ClassType.CLASS
        self.declare(stmt.name)
        self.define(stmt.name)
        self.begin_scope()
        self.scopes[-1]['this'] = Variable(stmt.name, VariableState.CLASS_NAME)
        for method in stmt.methods:
            declaration = FunctionType.METHOD
            if method.name.lexeme == 'init':
                declaration = FunctionType.INITIALIZER
            self.resolve_function(method, declaration)
        self.end_scope()
        self.current_class = enclosing_class

    def visit_function_stmt(self, stmt):
        self.declare(stmt.name)
        self.define(stmt.name)
        self.resolve_function(stmt, FunctionType.FUNCTION)

    def visit_if_stmt(self, stmt):
        self._resolve(stmt.condition)
        self._resolve(stmt.then_branch)
        if stmt.else_branch is not None:
            self._resolve(stmt.else_branch)

    def visit_var_stmt(self, stmt):
        self.declare(stmt.name)
        if stmt.initializer is not None:
            self._resolve(stmt.initializer)
        self.define(stmt.name)

    def visit_expression_stmt(self, stmt):
        self._resolve(stmt.expr)

    def visit_print_stmt(self, stmt):
        self._resolve(stmt.expr)

    def visit_return_stmt(self, stmt):
        if self.current_function is FunctionType.NONE:
            self.eh.error(stmt.keyword, 'Cannot return from top-level code')
        if stmt.value is not None:
            if self.current_function is FunctionType.INITIALIZER:
                self.eh.error(stmt.keyword, 'Cannot return a value from an initializer')
            self._resolve(stmt.value)

    def visit_while_stmt(self, stmt):
        self.inside_loop = True
        self._resolve(stmt.condition)
        self._resolve(stmt.body)
        self.inside_loop = False

    def visit_block_stmt(self, stmt):
        self.begin_scope()
        self.resolve(stmt.stmts)
        self.end_scope()

    def visit_break_stmt(self, stmt):
        if self.inside_loop == False:
            self.eh.errorT(stmt.name, 'Cannot break from top-level code')
        #self._resolve(stmt)

    def declare(self, name):
        if len(self.scopes) > 0:
            if name.lexeme in self.scopes[-1]:
                self.eh.errorT(name, 'Already variable with this name in this scope')
            # Add variable to innermost scope
            self.scopes[-1][name.lexeme] = Variable(name, VariableState.DECLARED)
    
    def define(self, name):
        if len(self.scopes) > 0:
            self.scopes[-1][name.lexeme] = Variable(name, VariableState.DEFINED)
    
    def resolve_function(self, function, type):
        enclosing_function = self.current_function
        self.current_function = type
        self.visit_function_expr(function.function)
        self.current_function = enclosing_function

    # Expressions
    def visit_function_expr(self, expr):
        self.begin_scope()
        for param in expr.params:
            self.declare(param)
            self.define(param)
        self.resolve(expr.body)
        self.end_scope()

    def visit_this_expr(self, expr):
        if self.current_class == ClassType.NONE:
            self.eh.error(expr.keyword, 'Cannot use "this" outside of a class')
            return None
        self.resolve_local(expr, expr.keyword, False)

    def visit_get_expr(self, expr):
        self._resolve(expr.object)

    def visit_set_expr(self, expr):
        self._resolve(expr.value)
        self._resolve(expr.object)
    
    def visit_logical_expr(self, expr):
        self._resolve(expr.left)
        self._resolve(expr.right)

    def visit_call_expr(self, expr):
        self._resolve(expr.callee)
        for arg in expr.arguments:
            self._resolve(arg)

    def visit_variable_expr(self, expr):
        if len(self.scopes) > 0 and expr.name.lexeme in self.scopes[-1]:
            if self.scopes[-1][expr.name.lexeme].state == VariableState.DECLARED:
                self.eh.errorT(expr.name, 'Cannot read local variable in its own initializer')
        self.resolve_local(expr, expr.name, True)

    def visit_assign_expr(self, expr):
        self._resolve(expr.value)
        self.resolve_local(expr, expr.name, False)

    def visit_binary_expr(self, expr):
        self._resolve(expr.left)
        self._resolve(expr.right)

    def visit_grouping_expr(self, expr):
        self._resolve(expr.expression)

    def visit_literal_expr(self, expr):
        return None

    def visit_unary_expr(self, expr):
        self._resolve(expr.right)

    def resolve_local(self, expr, name, is_read):
        i = len(self.scopes) - 1
        while i >= 0:
            if self.scopes[i].get(name.lexeme) is not None:
                self.interpreter.resolve(expr, len(self.scopes)-1-i)
                if is_read: 
                    self.scopes[i].get(name.lexeme).state = VariableState.READ
                return
            i = i - 1
