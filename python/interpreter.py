
from tokens import TokenKind
from common import RunTimeError, Return, BreakException, Environment, Visitor
from expr import *
from stmt import *
from function import *

class Interpreter(Visitor):
    def __init__(self):
        self.globals = Environment()
        self.env = self.globals
        # NOTE: Clock in a native function
        # TODO: Add function to interact with file, I\O etc.
        self.globals.define('clock', Clock())

    def interpret(self, stmts):
        if stmts is None:
            return
        for stmt in [s for s in stmts if s is not None]:
            yield self.execute(stmt)

    def stringify(self, obj):
        if obj is None:
            return 'nil'
        if isinstance(obj, float):
            t = str(obj)
            if t.endswith('.0'):
                return t[:-2]
        if isinstance(obj, str):
            return f'"{obj}"'
        return str(obj)
    
    def visit_function_stmt(self, stmt):
        name = stmt.name.lexeme
        func = LangFunction(name, stmt.function, self.env)
        self.env.define(name, func)
        return None
    
    def visit_function_expr(self, expr):
        return LangFunction('', expr, self.env)

    def visit_if_stmt(self, stmt):
        if self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.then_branch)
        else:
            self.execute(stmt.else_branch)
        return None
    
    def visit_var_stmt(self, stmt):
        value = None
        if stmt.initializer is not None:
            value = self.evaluate(stmt.initializer)
        self.env.define(stmt.name.lexeme, value)
        return None

    def visit_expression_stmt(self, stmt):
        return self.evaluate(stmt.expr)

    def visit_print_stmt(self, stmt):
        value = self.evaluate(stmt.expr)
        print(self.stringify(value))
    
    def visit_return_stmt(self, stmt):
        value = None
        if stmt is not None:
            value = self.evaluate(stmt.value)
        raise Return(value)

    def visit_while_stmt(self, stmt):
        try:
            while self.is_truthy(self.evaluate(stmt.condition)):
                self.execute(stmt.body)
        except BreakException:
            # DO NOTHING
            pass
        return None

    def visit_block_stmt(self, stmt):
        self.execute_block(stmt.stmts, Environment(self.env))
        return None
    
    def visit_break_stmt(self, stmt):
        raise BreakException(stmt.name)
    
    def visit_logical_expr(self, expr):
        left = self.evaluate(expr.left)
        if expr.operator.kind == TokenKind.OR:
            if self.is_truthy(left):
                return left
        else:
            # LOGICAL AND
            if not self.is_truthy(left):
                return left
        return self.evaluate(expr.right)
    
    def visit_call_expr(self, expr):
        callee = self.evaluate(expr.callee)
        args = [self.evaluate(arg) for arg in expr.arguments]
        if not isinstance(callee, LangCallable):
            raise RuntimeError(expr.paren, 'Can only call functions and classes')
        if len(args) != callee.arity():
            raise RuntimeError(expr.paren, f'Expected {callee.arity()} arguments but got {len(args)}')
        return callee.call(self, args)

    def visit_variable_expr(self, expr):
        value = self.env.get(expr.name)
        if value is not None:
            return value
        raise RunTimeError(expr.name, 'Accessing uninitialized variable')

    def visit_assignment_expr(self, expr):
        value = self.evaluate(expr.value)
        self.env.assign(expr.name, value)
        return value

    def visit_binary_expr(self, expr):
        right = self.evaluate(expr.right)
        left  = self.evaluate(expr.left)
        if expr.operator.kind == TokenKind.GREATER:
            self.check_number_operand(expr.operator, left, right)
            return float(left) > float(right)
        if expr.operator.kind == TokenKind.GREATER_EQUAL:
            self.check_number_operand(expr.operator, left, right)
            return float(left) >= float(right)
        if expr.operator.kind == TokenKind.LESS:
            self.check_number_operand(expr.operator, left, right)
            return float(left) < float(right)
        if expr.operator.kind == TokenKind.LESS_EQUAL:
            self.check_number_operand(expr.operator, left, right)
            return float(left) <= float(right)
        if expr.operator.kind == TokenKind.MINUS:
            self.check_number_operand(expr.operator, left, right)
            return float(left) - float(right)
        if expr.operator.kind == TokenKind.PLUS:
            if isinstance(left, float) and isinstance(right, float):
                return float(left) + float(right)
            if isinstance(left, str) and isinstance(right, str):
                return str(left) + str(right)
            if isinstance(left, str) and isinstance(right, float) or isinstance(left, float) and isinstance(right, str):
                if isinstance(left, float):
                    t = str(left)
                    return t[:-2] + str(right) if t.endswith('.0') else str(left) + str(right)
                if isinstance(right, float):
                    t = str(right)
                    return str(left) + t[:-2] if t.endswith('.0') else str(left) + str(right)
            raise RunTimeError(expr.operator, 'Operands must be two numbers or two strings')
        if expr.operator.kind == TokenKind.SLASH:
            self.check_number_operand(expr.operator, left, right)
            if float(right) == 0:
                raise RunTimeError(expr.operator, 'Cannot divide by zero')
            return float(left) / float(right)
        if expr.operator.kind == TokenKind.STAR:
            self.check_number_operand(expr.operator, left, right)
            return float(left) * float(right)
        if expr.operator.kind == TokenKind.BANG_EQUAL:
            return not self.is_equal(left, right)
        if expr.operator.kind == TokenKind.EQUAL_EQUAL:
            return self.is_equal(left, right)
        # Unreachable
        return None

    def visit_grouping_expr(self, expr):
        return self.evaluate(expr.expression)

    def visit_literal_expr(self, expr):
        return expr.value

    def visit_unary_expr(self, expr):
        right = self.evaluate(expr.right)
        if expr.operator.kind == TokenKind.BANG:
            return not self.is_truthy(right)
        if expr.operator.kind == TokenKind.MINUS:
            self.check_number_operand(expr.operator, right)
            return -float(right)
        # Unreachable
        return None

    def execute(self, stmt):
        if stmt is not None:
            return stmt.accept(self)

    def execute_block(self, stmts, env):
        prev = self.env
        try:
            self.env = env
            for stmt in stmts:
                self.execute(stmt)
        finally:
            self.env = prev

    def evaluate(self, expr):
        return expr.accept(self)

    def is_truthy(self, obj):
        if obj == None:
            return False
        if isinstance(obj, bool):
            return bool(obj)
        return True

    def is_equal(self, left, right):
        if left is None and right is None:
            return True
        return left == right

    def check_number_operand(self, operator, operand):
        if isinstance(operand, float):
            return 
        raise RunTimeError(operand, 'Operand must be a number')

    def check_number_operand(self, operator, left, right):
        if isinstance(left, float) and isinstance(right, float):
            return 
        raise RunTimeError(operator, 'Operands must be numbers')