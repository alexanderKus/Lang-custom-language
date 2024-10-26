from tokens import TokenKind, Token
from expr import *
from stmt import *
from function import *

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
            if self.match(TokenKind.CLASS):
                return self.class_declaration()
            if self.check(TokenKind.FUN) and self.check_next(TokenKind.IDENTIFIER):
                self.consume(TokenKind.FUN, '')
                return self.function('function');
            if self.match(TokenKind.VAR):
                return self.var_declaration()
            return self.statement()
        except ParseError:
            self.synchronize()
        return None
    
    def class_declaration(self):
        name = self.consume(TokenKind.IDENTIFIER, 'Expect class name')
        self.consume(TokenKind.LEFT_BRACE, 'Expect "{" before class body')
        methods = []
        while not self.check(TokenKind.RIGHT_BRACE) and not self.is_at_end():
            methods.append(self.function("method"))
        self.consume(TokenKind.RIGHT_BRACE, 'Expect "}" after class body')
        return ClassStmt(name, methods)
    
    def function(self, kind):
        name = self.consume(TokenKind.IDENTIFIER, f'Expect {kind} name')
        return FunctionStmt(name, self.function_body(kind))

    def function_body(self, kind):
        self.consume(TokenKind.LEFT_PAREN, f'Expect "(" after {kind} name')
        params = []
        if not self.check(TokenKind.RIGHT_PAREN):
            while True:
                if len(params) >= 8:
                    self.error(self.peek(), 'Cannot have more than 8 parameters')
                params.append(self.consume(TokenKind.IDENTIFIER, 'Expect parameter name')) 
                if not self.match(TokenKind.COMMA):
                    break
        self.consume(TokenKind.RIGHT_PAREN, 'Expect ")" after parameters')
        self.consume(TokenKind.LEFT_BRACE, 'Expect "{" before ' + kind + ' body')
        body = self.block()
        return FunctionExpr(params, body)
    
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
            elif isinstance(expr, GetExpr):
                return SetExpr(expr.object, expr.name, value)
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
            elif self.match(TokenKind.DOT):
                name = self.consume(TokenKind.IDENTIFIER, 'Expect property name after "."')
                expr = GetExpr(expr, name)
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
        if self.match(TokenKind.FUN):
            return self.function_body('function')
        if self.match(TokenKind.FALSE):
            return LiteralExpr(False)
        if self.match(TokenKind.TRUE):
            return LiteralExpr(True)
        if self.match(TokenKind.NIL):
            return LiteralExpr(None)
        if self.match(TokenKind.NUMBER, TokenKind.STRING):
            return LiteralExpr(self.previous().literal)
        if self.match(TokenKind.THIS):
            return ThisExpr(self.previous())
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
    
    def check_next(self, kind):
        if self.is_at_end() or (self.tokens[self.current+1] == TokenKind.EOF):
            return False
        return self.tokens[self.current+1].kind == kind
    
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