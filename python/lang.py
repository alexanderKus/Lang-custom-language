#!/usr/bin/python3

import sys
from enum import Enum

class RunTimeError(Exception):
    def __init__(self, token, message):
        super().__init__(message)
        self.token = token

class Return(Exception):
    def __init__(self, value):
        self.value = value

class BreakException(RunTimeError):
    def __init__(self, token, message='Must be inside a loop to use "break"'):
        super().__init__(token, message)

class Environment:
    def __init__(self, enclosing = None):
        self.enclosing = enclosing
        self.values = {}
    
    def define(self, name, value):
        self.values[name] = value

    def get(self, token):
        if token.lexeme in self.values:
            return self.values.get(token.lexeme)
        if self.enclosing is not None:
            return self.enclosing.get(token)
        raise RunTimeError(token, f'Undefined variable {token.lexeme}')

    def assign(self, token, value):
        if token.lexeme in self.values:
            self.values[token.lexeme] = value
            return
        if self.enclosing is not None:
            self.enclosing.assign(token, value)
            return
        raise RunTimeError(token, f'Undefined variable "{token.lexeme}"')

class Interpreter:
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
        func = LangFunction(stmt)
        self.env.define(stmt.name.lexeme, func)
        return None

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

class ParseError(Exception):
    pass

class Parser:
    def __init__(self, tokens, eh):
        self.tokens = tokens
        self.eh = eh
        self.current = 0
        self.loop_depth = 0

    def parse(self):
        try:
            stmts = []
            while not self.is_at_end():
                s = self.declaration()
                if s is not None:
                    stmts.append(s)
            return stmts
        except ParseError:
            return None
    
    def declaration(self):
        try:
            if self.match(TokenKind.FUN):
                return self.function('function');
            if self.match(TokenKind.VAR):
                return self.var_declaration()
            return self.statement()
        except ParseError:
            self.synchronize()
        return None
    
    def function(self, kind):
        name = self.consume(TokenKind.IDENTIFIER, f'Expect {kind} name')
        self.consume(TokenKind.LEFT_PAREN, f'Expect "(" after {kind} name')
        params = []
        if not self.check(TokenKind.RIGHT_PAREN):
            while True:
                if len(params) >= 255:
                    self.error(self.peek(), 'Cannot have more than 255 parameters')
                params.append(self.consume(TokenKind.IDENTIFIER, 'Expect parameter name')) 
                if not self.match(TokenKind.COMMA):
                    break
        self.consume(TokenKind.RIGHT_PAREN, 'Expect ")" after parameters')
        self.consume(TokenKind.LEFT_BRACE, 'Expect "{" before ' + kind + ' body')
        body = self.block()
        return FunctionStmt(name, params, body)
    
    def var_declaration(self):
        name = self.consume(TokenKind.IDENTIFIER, 'Expect variable name')
        initializer = None
        if self.match(TokenKind.EQUAL):
            initializer = self.expression()
        self.consume(TokenKind.SEMICOLON, 'Expect ";" after variable declaration')
        return VarStmt(name, initializer)

    def statement(self):
        if self.match(TokenKind.FOR):
            return self.for_statement()
        if self.match(TokenKind.IF):
            return self.if_statement()
        if self.match(TokenKind.PRINT):
            return self.print_statement()
        if self.match(TokenKind.RETURN):
            return self.return_statement()
        if self.match(TokenKind.WHILE):
            return self.while_statement()
        if self.match(TokenKind.LEFT_BRACE):
            return BlockStmt(self.block())
        if self.match(TokenKind.BREAK):
            return self.break_statement()
        return self.expression_statement()
    
    def for_statement(self):
        # For loop is syntactic sugar of while loop,
        # so, for loop is desugar into while loop
        self.consume(TokenKind.LEFT_PAREN, 'Expect "(" after "for"')
        initializer = None
        if self.match(TokenKind.SEMICOLON):
            # initializer = None
            pass
        elif self.match(TokenKind.VAR):
            initializer = self.var_declaration()
        else:
            initializer = self.expression_statement()
        condition = None
        if not self.check(TokenKind.SEMICOLON):
            condition = self.expression()
        self.consume(TokenKind.SEMICOLON, 'Expect ";" after loop condition')
        increment = None
        if not self.check(TokenKind.RIGHT_PAREN):
            increment = self.expression()
        self.consume(TokenKind.RIGHT_PAREN, 'Expect ")" after for clauses')
        try:
            self.loop_depth += 1
            body = self.statement()
            if increment is not None:
                body = BlockStmt([body, ExpressionStmt(increment)])
            if condition is None:
                condition = LiteralExpr(True)
            body = WhileStmt(condition, body)
            if initializer is not None:
                body = BlockStmt([initializer, body])
            return body
        finally:
            self.loop_depth -= 1
    
    def if_statement(self):
        self.consume(TokenKind.LEFT_PAREN, 'Expect "(" after "if"')
        condition = self.expression()
        self.consume(TokenKind.RIGHT_PAREN, 'Expect ")" after if condition')
        then_branch = self.statement()
        else_branch = None
        if (self.match(TokenKind.ELSE)):
            else_branch = self.statement()
        return IfStmt(condition, then_branch, else_branch)

    def print_statement(self):
        value = self.expression()
        self.consume(TokenKind.SEMICOLON, 'Expect ";" after value')
        return PrintStmt(value)
    
    def return_statement(self):
        keyword = self.previous()
        value = None
        if not self.check(TokenKind.SEMICOLON):
            value = self.expression()
        self.consume(TokenKind.SEMICOLON, 'Expect ";" after return value')
        return ReturnStmt(keyword, value)
    
    def while_statement(self):
        self.consume(TokenKind.LEFT_PAREN, 'Expect "(" after "while"')
        expr = self.expression()
        self.consume(TokenKind.RIGHT_PAREN, 'Expect ")" after "while"')
        try:
            self.loop_depth += 1
            stmt = self.statement()
            return WhileStmt(expr, stmt)
        finally:
            self.loop_depth -= 1

    def block(self):
        stmts = []
        while not self.check(TokenKind.RIGHT_BRACE) and not self.is_at_end():
            stmts.append(self.declaration())
        self.consume(TokenKind.RIGHT_BRACE, 'Expect } after block')
        return stmts
    
    def break_statement(self):
        if self.loop_depth == 0:
            self.error(self.previous(), 'Must be inside a loop to use "break"')
        name = self.previous()
        self.consume(TokenKind.SEMICOLON, 'Expect ";" after "break"')
        return BreakStmt(name)

    def expression_statement(self):
        value = self.expression()
        self.consume(TokenKind.SEMICOLON, 'Expected ";" after expression')
        return ExpressionStmt(value)

    def expression(self):
        return self.assignment()
    
    def assignment(self):
        expr = self.or_f()
        if self.match(TokenKind.EQUAL):
            equals = self.previous()
            value = self.assignment()
            if isinstance(expr, VariableExpr):
                return AssignExpr(expr.name, value)
            self.error(equals, 'Invalid assignment target')
        return expr
    
    def or_f(self):
        expr = self.and_f()
        while self.match(TokenKind.OR):
            operator = self.previous()
            right = self.and_f()
            expr = LogicalExpr(expr, operator, right)
        return expr
    
    def and_f(self):
        expr = self.equality()
        while self.match(TokenKind.AND):
            operator = self.previous()
            right = self.equality()
            expr = LogicalExpr(expr, operator, right)
        return expr

    def equality(self):
        expr = self.comparison()
        while self.match(TokenKind.BANG_EQUAL, TokenKind.EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expr = BinaryExpr(expr, operator, right)
        return expr

    def comparison(self):
        expr = self.term()
        while self.match(TokenKind.GREATER, TokenKind.GREATER_EQUAL, TokenKind.LESS, TokenKind.LESS_EQUAL):
            operator = self.previous()
            right = self.term()
            expr = BinaryExpr(expr, operator, right)
        return expr

    def term(self):
        expr = self.factor()
        while self.match(TokenKind.MINUS, TokenKind.PLUS):
            operator = self.previous()
            right = self.factor()
            expr = BinaryExpr(expr, operator, right)
        return expr

    def factor(self):
        expr = self.unary()
        while self.match(TokenKind.SLASH, TokenKind.STAR):
            operator = self.previous()
            right = self.unary()
            expr = BinaryExpr(expr, operator, right)
        return expr

    def unary(self):
        if self.match(TokenKind.BANG, TokenKind.MINUS):
            operator = self.previous()
            right = self.unary()
            return UnaryExpr(operator, right)
        return self.call()
    
    def call(self):
        expr = self.primary()
        while True:
            if self.match(TokenKind.LEFT_PAREN):
                expr = self.finish_call(expr)
            else:
                break
        return expr
    
    def finish_call(self, callee):
        args = []
        if not self.check(TokenKind.RIGHT_PAREN):
            args.append(self.expression())
            while self.match(TokenKind.COMMA):
                if len(args) >= 255:
                    self.eh.error(self.peek(), 'Cannot have more then 255 arguments')
                args.append(self.expression())
        paren = self.consume(TokenKind.RIGHT_PAREN, 'Expect ")" after arguments')
        return CallExpr(callee, paren, args)

    def primary(self):
        if self.match(TokenKind.FALSE):
            return LiteralExpr(False)
        if self.match(TokenKind.TRUE):
            return LiteralExpr(True)
        if self.match(TokenKind.NIL):
            return LiteralExpr(None)
        if self.match(TokenKind.NUMBER, TokenKind.STRING):
            return LiteralExpr(self.previous().literal)
        if self.match(TokenKind.IDENTIFIER):
            return VariableExpr(self.previous())
        if self.match(TokenKind.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenKind.RIGHT_PAREN, 'Expect ")" after expression')
            return GroupingExpr(expr)
        raise self.error(self.peek(), 'Expect expression')

    def match(self, *token_kinds):
        for token_kind in token_kinds:
            if self.check(token_kind):
                self.advance()
                return True
        return False

    def advance(self):
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def previous(self):
        return self.tokens[self.current-1]

    def peek(self):
        return self.tokens[self.current]

    def is_at_end(self):
        return self.peek().kind == TokenKind.EOF

    def consume(self, kind, message):
        if self.check(kind):
            return self.advance()
        raise self.error(self.peek(), message)

    def check(self, kind):
        if self.is_at_end():
            return False
        return self.peek().kind == kind
    
    def error(self, token, message):
        self.eh.errorT(token, message)
        return ParseError()

    def synchronize(self):
        self.advance()
        while not self.is_at_end():
            if self.previous().kind == TokenKind.SEMICOLON:
                return
            if self.peek() in [TokenKind.CLASS, TokenKind.FUN, TokenKind.VAR, 
                                TokenKind.FOR, TokenKind.IF, TokenKind.WHILE, 
                                TokenKind.PRINT, TokenKind.RETURN]:
                return
            self.advance()

class LangCallable:
    def call(self, interpreter, arguments):
        pass

    def arity(self):
        pass

class Clock(LangCallable):
    def __str__(self):
        return '<native function>'

    def call(self, interpreter, arguments):
        import time
        return time.time()

    def arity(self):
        return 0

class LangFunction(LangCallable):
    def __init__(self, declaration):
        self.declaration = declaration
    
    def __str__(self):
        return f'<fn {self.declaration.name.lexeme}>'

    def call(self, interpreter, arguments):
        env = Environment(interpreter.globals)
        for i in range(len(self.declaration.params)):
            env.define(self.declaration.params[i].lexeme, arguments[i])
        try:
            interpreter.execute_block(self.declaration.body, env)
        except Return as r:
            return r.value
        return None

    def arity(self):
        return len(self.declaration.params)

class FunctionStmt:
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body

    def accept(self, visitor):
        return visitor.visit_function_stmt(self)

class ReturnStmt:
    def __init__(self, keyword, value):
        self.keyword = keyword
        self.value = value

    def accept(self, visitor):
        return visitor.visit_return_stmt(self)

class WhileStmt:
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def accept(self, visitor):
        return visitor.visit_while_stmt(self)

class IfStmt:
    def __init__(self, condition, then_branch, else_branch):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    def accept(self, visitor):
        return visitor.visit_if_stmt(self)

class BlockStmt:
    def __init__(self, stmts):
        self.stmts = stmts

    def accept(self, visitor):
        return visitor.visit_block_stmt(self)

class VarStmt:
    def __init__(self, name, initializer):
        self.name = name
        self.initializer = initializer

    def accept(self, visitor):
        return visitor.visit_var_stmt(self)

class ExpressionStmt:
    def __init__(self, expr):
        self.expr = expr

    def accept(self, visitor):
        return visitor.visit_expression_stmt(self)

class PrintStmt:
    def __init__(self, expr):
        self.expr = expr

    def accept(self, visitor):
        return visitor.visit_print_stmt(self)

class BreakStmt:
    def __init__(self, name):
        self.name = name

    def accept(self, visitor):
        return visitor.visit_break_stmt(self)

class CallExpr:
    def __init__(self, callee, token, arguments):
        self.callee = callee
        self.token = token
        self.arguments = arguments

    def accept(self, visitor):
        return visitor.visit_call_expr(self)
    
class LogicalExpr:
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor):
        return visitor.visit_logical_expr(self)

class AssignExpr:
    def __init__(self, name, value):
        self.name = name
        self.value = value
        
    def accept(self, visitor):
        return visitor.visit_assignment_expr(self)

class BinaryExpr:
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor):
        return visitor.visit_binary_expr(self)

class GroupingExpr:
    def __init__(self, expression):
        self.expression = expression

    def accept(self, visitor):
        return visitor.visit_grouping_expr(self)

class LiteralExpr:
    def __init__(self, value):
        self.value = value

    def accept(self, visitor):
        return visitor.visit_literal_expr(self)

class UnaryExpr:
    def __init__(self, operator, right):
        self.operator = operator
        self.right = right

    def accept(self, visitor):
        return visitor.visit_unary_expr(self)

class VariableExpr:
    def __init__(self, name):
        self.name = name

    def accept(self, visitor):
        return visitor.visit_variable_expr(self)

class TokenKind(Enum):
    # Single-character tokens.
    LEFT_PAREN = 0,
    RIGHT_PAREN = 1,
    LEFT_BRACE = 2,
    RIGHT_BRACE = 3,
    COMMA = 4,
    DOT = 5,
    MINUS = 6,
    PLUS = 7,
    SEMICOLON = 8,
    SLASH = 9,
    STAR = 10,

    # One or two character tokens.
    BANG = 11,
    BANG_EQUAL = 12,
    EQUAL = 13,
    EQUAL_EQUAL = 14,
    GREATER = 15,
    GREATER_EQUAL = 16,
    LESS = 17
    LESS_EQUAL = 18,

    # Literals.
    IDENTIFIER = 19,
    STRING = 20,
    NUMBER = 21

    # Keywords.
    AND = 22,
    CLASS = 23,
    ELSE = 24,
    FALSE = 25,
    FUN = 26,
    FOR = 27,
    IF = 28,
    NIL = 29,
    OR = 30,
    PRINT = 31,
    RETURN = 32,
    SUPER = 33,
    THIS = 34,
    TRUE = 35
    VAR = 36,
    WHILE = 37,
    BREAK = 38

    EOF = 39

class Token:
    def __init__(self, kind, lexeme, literal, line):
        self.kind = kind
        self.lexeme = lexeme
        self.literal = literal
        self.line = line

    def _str__(self):
        return f'TOKEN: {self.kind} {self.lexeme} {self.literal}'

class Lexer:
    def __init__(self, source_code, eh):
        self.source_code = source_code
        self.eh = eh
        self.start = 0
        self.current = 0
        self.line = 1
        self.tokens = []
        self.keywords = {
            'and': TokenKind.AND,
            'class': TokenKind.CLASS,
            'else': TokenKind.ELSE,
            'false': TokenKind.FALSE,
            'for': TokenKind.FOR,
            'fun': TokenKind.FUN,
            'if': TokenKind.IF,
            'nil': TokenKind.NIL,
            'or': TokenKind.OR,
            'print': TokenKind.PRINT,
            'return': TokenKind.RETURN,
            'super': TokenKind.SUPER,
            'this': TokenKind.THIS,
            'true': TokenKind.TRUE,
            'var': TokenKind.VAR,
            'while': TokenKind.WHILE,
            'break': TokenKind.BREAK
        }

    def tokenize(self):
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()
        self.tokens.append(Token(TokenKind.EOF, '', None, self.line))
        return self.tokens

    def is_at_end(self):
        return self.current >= len(self.source_code)

    def scan_token(self):
        c = self.advance()
        if c == '(':
            self.add_token(TokenKind.LEFT_PAREN, None)
        elif c == ')':
            self.add_token(TokenKind.RIGHT_PAREN, None)
        elif c == '{':
            self.add_token(TokenKind.LEFT_BRACE, None)
        elif c == '}':
            self.add_token(TokenKind.RIGHT_BRACE, None)
        elif c == ',':
            self.add_token(TokenKind.COMMA, None)
        elif c == '.':
            self.add_token(TokenKind.DOT, None)
        elif c == '-':
            self.add_token(TokenKind.MINUS, None)
        elif c == '+':
            self.add_token(TokenKind.PLUS, None)
        elif c == ';':
            self.add_token(TokenKind.SEMICOLON, None)
        elif c == '*':
            self.add_token(TokenKind.STAR, None)
        elif c == '!':
            self.add_token(TokenKind.BANG_EQUAL if self.match('=') else TokenKind.BANG, None)
        elif c == '=':
            self.add_token(TokenKind.EQUAL_EQUAL if self.match('=') else TokenKind.EQUAL, None)
        elif c == '<':
            self.add_token(TokenKind.LESS_EQUAL if self.match('=') else TokenKind.LESS, None)
        elif c == '>':
            self.add_token(TokenKind.GREATER_EQUAL if self.match('=') else TokenKind.GREATER, None)
        elif c == '/':
            if self.match('/'):
                while self.peek() != '\n' and not self.is_at_end():
                    self.advance()
            elif self.match('*'): 
                while self.peek() != '*' and self.next_peek() != '/' and not self.is_at_end():
                    if self.peek() == '\n':
                        self.line += 1
                    self.advance()
                self.advance() # eat *
                self.advance() # eat /
            else:
                self.add_token(TokenKind.SLASH, None)
        elif c == ' ' or c == '\b' or c == '\r':
            # Skipping white spaces
            pass
        elif c == '\n':
            self.line += 1
        elif c == '"':
            self.string()
        elif self.is_digit(c):
            self.number()
        elif self.is_alpha(c):
            self.identifier()
        else:
            self.eh.error(self.line, 'Unexpected character.')

    def advance(self):
        self.current += 1
        return self.source_code[self.current-1]
    
    def match(self, expected):
        if self.is_at_end():
            return False
        if self.source_code[self.current] != expected:
            return False
        self.current += 1
        return True

    def peek(self):
        if self.is_at_end():
            return '\0'
        return self.source_code[self.current]

    def next_peek(self):
        if self.current + 1 >= len(self.source_code):
            return '\0'
        return self.source_code[self.current+1]

    def string(self):
        while self.peek() != '"' and not self.is_at_end():
            if self.peek() == '\n':
                self.line += 1
            self.advance()
        if self.is_at_end():
            self.eh.error(self.line, 'Unterminated string.')
            return
        self.advance()
        value = self.source_code[self.start+1:self.current-1]
        self.add_token(TokenKind.STRING, value)

    def number(self):
        while self.is_digit(self.peek()):
            self.advance()
        if self.peek() == '.' and self.is_digit(self.next_peek()):
            self.advance()
            while self.is_digit(self.peek()):
                self.advance()
        self.add_token(TokenKind.NUMBER, float(self.source_code[self.start:self.current]))

    def identifier(self):
        while self.is_alpha_numeric(self.peek()):
            self.advance()
        text = self.source_code[self.start:self.current]
        type_ = self.keywords.get(text)
        if type_ is not None:
            self.add_token(type_, None)
        else:
            self.add_token(TokenKind.IDENTIFIER, None)

    def is_alpha(self, c):
        return (c >= 'a' and c <= 'z') or (c >= 'A' and c <= 'Z') or (c == '_')

    def is_digit(self, c):
        return c >= '0' and c <= '9'

    def is_alpha_numeric(self, c):
        return self.is_alpha(c) or self.is_digit(c)

    def add_token(self, kind, literal):
        text = self.source_code[self.start:self.current]
        self.tokens.append(Token(kind, text, literal, self.line))

class Lang:
    def __init__(self):
        self.interpreter = Interpreter()
        self.eh = ErrorHandler(self)
        self.had_error = False
        self.had_runtime_error = False

    def run_prompt(self):
        while True:
            line = input('> ')
            if line != '' and line != None:
                self.run(line)
                self.had_error = False

    def run_file(self, source_file):
        source_code = ''
        try:
            with open(source_file, 'r') as f:
                source_code = f.read()
        except FileNotFoundError:
            self.eh.error(0, f'cannot open {source_file}')
            exit(68)
        self.run(source_code)
        if self.had_error:
            exit(69)
        if self.had_runtime_error:
            exit(70)

    def run(self, source_code):
        if source_code == 'exit()':
            exit(0)
        lexer = Lexer(source_code, self.eh)
        tokens = lexer.tokenize()
        parser = Parser(tokens, self.eh)
        stmts = parser.parse()
        if self.had_error:
            return
        # NOTE: sometimes stmts may contains None values,
        # skipping them may be a good idea, to run interpreter on valid statements
        try:
            gen = self.interpreter.interpret(stmts)
            for v in [g for g in gen if g is not None]:
                print(v)
        except RunTimeError as e:
            self.eh.runtime_error(e)

class ErrorHandler:
    def __init__(self, lang):
        self.lang = lang

    def error(self, line_number, message):
        self.report(line_number, '', message)

    def errorT(self, token, message):
        if token.kind == TokenKind.EOF:
            self.report(token.line, 'at end', message)
        else:
            self.report(token.line, f'at "{token.lexeme}"', message)

    def report(self, line, where, message):
        self.lang.had_error = True
        # TODO: come up with better error handling
        if line == 0 and where == '':
            print(f'ERROR: {message}')
        else:
            print(f'[Line {line}] ERROR: {where} {message}')
        
    def runtime_error(self, ex):
        self.lang.had_runtime_error = True
        print(f'[Line {ex.token.line}] {ex}')

if __name__ == '__main__':
    lang = Lang()
    if len(sys.argv) > 2:
        print("ERROR: USAGE 'main.py <source file>'")
        exit(69)
    elif len(sys.argv) == 2:
        source_file = sys.argv[1]
        lang.run_file(source_file)
    else:
        lang.run_prompt()
