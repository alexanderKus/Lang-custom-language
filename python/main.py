#!/usr/bin/python3

import sys
from enum import Enum


# GRAMMER
#
# expression -> equality ;
# equality   -> comparison ( ( "!=" | "==" ) comparison )* ;
# comparison -> term ( ( ">" | ">=" | ">" | ">=" ) term _* ;
# term       -> factor ( ( "-" | "+" ) factor )* ;
# factor     -> unary ( ( "/" | "*" ) unary )* ;
# unary      -> ( "!" | "-" ) unary
#               | primary ;
# primary    -> NUMBER | STRING | "true" | "false" | "nil"
#               | "(" expression ")" ;

class RunTimeError(Exception):
    def __init__(self, token, message):
        super().__init__(message)
        self.token = token

class Interpreter:
    def __init__(self):
        pass

    def interpret(self, expr):
            value = self._evaluate(expr)
            print(self._stringify(value))

    def _stringify(self, obj):
        if obj is None:
            return 'nil'
        if isinstance(obj, float):
            t = str(obj)
            if t.endswith('.0'):
                return t[:-2]
        return str(obj)
    
    def visit_binary_expr(self, expr):
        right = self._evaluate(expr.right)
        left  = self._evaluate(expr.left)
        if expr.operator.kind == TokenKind.GREATER:
            self._check_number_operand(expr.operator, left, right)
            return float(left) > float(right)
        if expr.operator.kind == TokenKind.GREATER_EQUAL:
            self._check_number_operand(expr.operator, left, right)
            return float(left) >= float(right)
        if expr.operator.kind == TokenKind.LESS:
            self._check_number_operand(expr.operator, left, right)
            return float(left) < float(right)
        if expr.operator.kind == TokenKind.LESS_EQUAL:
            self._check_number_operand(expr.operator, left, right)
            return float(left) <= float(right)
        if expr.operator.kind == TokenKind.MINUS:
            self._check_number_operand(expr.operator, left, right)
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
            self._check_number_operand(expr.operator, left, right)
            if float(right) == 0:
                raise RunTimeError(expr.operator, 'Cannot devide by zero')
            return float(left) / float(right)
        if expr.operator.kind == TokenKind.STAR:
            self._check_number_operand(expr.operator, left, right)
            return float(left) * float(right)
        if expr.operator.kind == TokenKind.BANG_EQUAL:
            return not self._is_equal(left, right)
        if expr.operator.kind == TokenKind.EQUAL_EQUAL:
            return self._is_equal(left, right)
        # Unreachable
        return None

    def visit_grouping_expr(self, expr):
        return self._evaluate(expr.expression)

    def visit_literal_expr(self, expr):
        return expr.value

    def visit_unary_expr(self, expr):
        right = self._evaluate(expr.right)
        if expr.operator.kind == TokenKind.BANG:
            return not self._is_truthy(right)
        if expr.operator.kind == TokenKind.MINUS:
            self._check_number_operand(expr.operator, right)
            return -float(right)
        # Unreachable
        return None

    def _evaluate(self, expr):
        return expr.accept(self)

    def _is_truthy(self, obj):
        if obj == None:
            return False
        if isinstance(obj, bool):
            return bool(obj)
        return True

    def _is_equal(left, right):
        if left is None and right is None:
            return True
        return left is right

    def _check_number_operand(self, operator, operand):
        if isinstance(operand, float):
            return 
        raise RunTimeError(operand, 'Operand must be a number')

    def _check_number_operand(self, operator, left, right):
        if isinstance(left, float) and isinstance(right, float):
            return 
        raise RunTimeError(operator, 'Operands must be numbers')

class ParseError(Exception):
    pass

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0

    def parse(self):
        try:
            return self._expression()
        except ParseError:
            return None

    def _expression(self):
        return self._equality()

    def _equality(self):
        expr = self._comparison()
        while self._match(TokenKind.BANG_EQUAL, TokenKind.EQUAL_EQUAL):
            operator = self._previous()
            right = self._comparison()
            expr = BinaryExpr(expr, operator, right)
        return expr

    def _comparison(self):
        expr = self._term()
        while self._match(TokenKind.GREATER, TokenKind.GREATER_EQUAL, TokenKind.LESS, TokenKind.LESS_EQUAL):
            operator = self._previous()
            right = self._term()
            expr = BinaryExpr(expr, operator, right)
        return expr

    def _term(self):
        expr = self._factor()
        while self._match(TokenKind.MINUS, TokenKind.PLUS):
            operator = self._previous()
            right = self._factor()
            expr = BinaryExpr(expr, operator, right)
        return expr

    def _factor(self):
        expr = self._unary()
        while self._match(TokenKind.SLASH, TokenKind.STAR):
            operator = self._previous()
            right = self._unary()
            expr = BinaryExpr(expr, operator, right)
        return expr

    def _unary(self):
        if self._match(TokenKind.BANG, TokenKind.MINUS):
            operator = self._previous()
            right = self._unary()
            return UnaryExpr(operator, right)
        return self._primary()

    def _primary(self):
        if self._match(TokenKind.FALSE):
            return LiteralExpr(False)
        if self._match(TokenKind.TRUE):
            return LiteralExpr(True)
        if self._match(TokenKind.NIL):
            return LiteralExpr(None)
        if self._match(TokenKind.NUMBER, TokenKind.STRING):
            return LiteralExpr(self._previous().literal)
        if self._match(TokenKind.LEFT_PAREN):
            expr = self._expression()
            self._consume(TokenKind.RIGHT_PAREN, 'Expect ")" after expression')
            return GroupingExpr(expr)
        raise self._error(self._peek(), 'Expect expression')

    def _match(self, *token_kinds):
        for token_kind in token_kinds:
            if self._check(token_kind):
                self._advance()
                return True
        return False

    def _advance(self):
        if not self._is_at_end():
            self.current += 1
        return self._previous()

    def _previous(self):
        return self.tokens[self.current-1]

    def _peek(self):
        return self.tokens[self.current]

    def _is_at_end(self):
        return self._peek().kind == TokenKind.EOF

    def _consume(self, kind, message):
        if self._check(kind):
            return self._advance()
        raise self._error(self._peek(), message)

    def _check(self, kind):
        if self._is_at_end():
            return False
        return self._peek().kind == kind
    
    def _error(self, token, message):
        ErrorHandler.errorT(token, message)
        return ParseError()

    def _synchronize(self):
        self._advance()
        while not self._is_at_end():
            if self._previous().kind == TokenKind.SEMICOLON:
                return
            if self._peek() in [TokenKind.CLASS, TokenKind.FUN, TokenKind.VAR, 
                                TokenKind.FOR, TokenKind.IF, TokenKind.WHILE, 
                                TokenKind.PRINT, TokenKind.RETURN]:
                return
            self._advance()

# class Visitor:
#     def visit_binary_expr(self, expr):
#         pass
# 
#     def visit_grouping_expr(self, expr):
#         pass
# 
#     def visit_literal_expr(self, xpr):
#         pass
# 
#     def visit_unary_expr(self, expr):
#         pass

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

class AstPrinter:
    def print(self, expr):
        return expr.accept(self)

    def visit_binary_expr(self, expr):
        return self._parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visit_grouping_expr(self, expr):
        return self._parenthesize('group', expr.expression)

    def visit_literal_expr(self, expr):
        if expr.value == 'nil':
            return 'nil'
        return str(expr.value)

    def visit_unary_expr(self, expr):
        return self._parenthesize(expr.operator.lexeme, expr.right)
    
    def _parenthesize(self, name, *exprs):
        result = '('
        result += name 
        for expr in exprs:
            result += ' ' 
            result += expr.accept(self)
        result += ')'
        return result

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

    EOF = 38

class Token:
    def __init__(self, kind, lexeme, literal, line):
        self.kind = kind
        self.lexeme = lexeme
        self.literal = literal
        self.line = line

    def __str__(self):
        return f'TOKEN: {self.kind} {self.lexeme} {self.literal}'

class Lexer:
    def __init__(self, source_code):
        self.source_code = source_code
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
            'while': TokenKind.WHILE
        }

    def tokenize(self):
        while not self._is_at_end():
            self.start = self.current
            self._scan_token()

        self.tokens.append(Token(TokenKind.EOF, '', None, self.line))
        return self.tokens

    def _is_at_end(self):
        return self.current >= len(self.source_code)

    def _scan_token(self):
        c = self._advance()
        if c == '(':
            self._add_token(TokenKind.LEFT_PAREN, None)
        elif c == ')':
            self._add_token(TokenKind.RIGHT_PAREN, None)
        elif c == '{':
            self._add_token(TokenKind.LEFT_BRACE, None)
        elif c == '}':
            self._add_token(TokenKind.RIGHT_BRACE, None)
        elif c == ',':
            self._add_token(TokenKind.COMMA, None)
        elif c == '.':
            self._add_token(TokenKind.DOT, None)
        elif c == '-':
            self._add_token(TokenKind.MINUS, None)
        elif c == '+':
            self._add_token(TokenKind.PLUS, None)
        elif c == ';':
            self._add_token(TokenKind.SEMICOLON, None)
        elif c == '*':
            self._add_token(TokenKind.STAR, None)
        elif c == '!':
            self._add_token(TokenKind.BANG_EQUAL if self._match('=') else TokenKind.BANG, None)
        elif c == '=':
            self._add_token(TokenKind.EQUAL_EQUAL if self._match('=') else TokenKind.EQUAL, None)
        elif c == '<':
            self._add_token(TokenKind.LESS_EQUAL if self._match('=') else TokenKind.LESS, None)
        elif c == '>':
            self._add_token(TokenKind.GREATED_EQUAL if self._match('=') else TokenKind.GREATED, None)
        elif c == '/':
            if self._match('/'):
                while self._peek() != '\n' and not self._is_at_end():
                    self._advance()
            elif self._match('*'): 
                while self._peek() != '*' and self._next_peek() != '/' and not self._is_at_end():
                    if self._peek() == '\n':
                        self.line += 1
                    self._advance()
                self._advance() # eat *
                self._advance() # eat /
            else:
                self._add_token(TokenKind.SLASH, None)
        elif c == ' ' or c == '\b' or c == '\r':
            # Skipping white spaces
            pass
        elif c == '\n':
            self.line += 1
        elif c == '"':
            self._string()
        elif self._is_digit(c):
            self._number()
        elif self._is_alpha(c):
            self._identifier()
        else:
            ErrorHandler.error(self.line, 'Unexpected character.')

    def _advance(self):
        self.current += 1
        return self.source_code[self.current-1]
    
    def _match(self, expected):
        if self._is_at_end():
            return False
        if self.source_code[self.current] != expected:
            return False

        self.current += 1
        return True

        return self.source_code[self.current]

    def _peek(self):
        if self._is_at_end():
            return '\0'
        return self.source_code[self.current]

    def _next_peek(self):
        if self.current + 1 >= len(self.source_code):
            return '\0'
        return self.source_code[self.current+1]

    def _string(self):
        while self._peek() != '"' and not self._is_at_end():
            if self._peek() == '\n':
                self.line += 1
            self._advance()
        if self._is_at_end():
            ErrorHandler.error(self.line, 'Unterminated string.')
            return
        self._advance()
        value = self.source_code[self.start+1:self.current-1]
        self._add_token(TokenKind.STRING, value)

    def _number(self):
        while self._is_digit(self._peek()):
            self._advance()
        if self._peek() == '.' and self._is_digit(self._next_peek()):
            self._advance()
            while self._is_digit(self._peek()):
                self._advance()
        self._add_token(TokenKind.NUMBER, float(self.source_code[self.start:self.current]))

    def _identifier(self):
        while self._is_alpha_numeric(self._peek()):
            self._advance()
        text = self.source_code[self.start:self.current]
        type_ = self.keywords.get(text)
        if type_ is not None:
            self._add_token(type_, None)
        else:
            self._add_token(TokenKind.IDENTIFIER, None)

    def _is_alpha(self, c):
        return (c >= 'a' and c <= 'z') or (c >= 'A' and c <= 'Z') or (c == '_')

    def _is_digit(selft, c):
        return c >= '0' and c <= '9'

    def _is_alpha_numeric(self, c):
        return self._is_alpha(c) or self._is_digit(c)

    def _add_token(self, kind, literal):
        text = self.source_code[self.start:self.current]
        self.tokens.append(Token(kind, text, literal, self.line))

class Lang:
    def __init__(self):
        self.interpreter = Interpreter()
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
        with open(source_file, 'r') as f:
            souce_code = f.read()
        if self.had_error or self.had_runtime_error:
            exit(69)
        self.run(souce_code)

    def run(self, source_code):
        if source_code == 'exit()':
            exit(0)

        lexer = Lexer(source_code)
        tokens = lexer.tokenize()

        parser = Parser(tokens)
        expr = parser.parse()

        if self.had_error:
            return
        
        try:
            self.interpreter.interpret(expr)
        except RunTimeError as e:
            self._runtime_error(e)

    def _error(self, line_number, message):
        self._report(line_number, '', message)

    def _report(self, line, where, message):
        ErrorHandler.report(line, where, massage)
        self.had_error = True

    def _runtime_error(self, ex):
        ErrorHandler.runtime_error(ex)
        self.had_runtime_error = True

class ErrorHandler:
    @staticmethod
    def error(line_number, message):
        ErrorHandler.report(line_number, '', message)

    @staticmethod
    def errorT(token, message):
        if token.kind == TokenKind.EOF:
            ErrorHandler.report(token.line, 'at end', message)
        else:
            ErrorHandler.report(token.line, f'at "{token.lexeme}"', message)

    @staticmethod
    def report(line, where, message):
        # TODO: come up with better error handling
        print(f'[Line {line}] ERROR: {where} {message}')
        
    @staticmethod
    def runtime_error(ex):
        print(f'{ex}\n[Line {ex.token.line}]')

if __name__ == '__main__':
    # expression = BinaryExpr(
    #         UnaryExpr(
    #             Token(TokenKind.MINUS, '-', None, 1),
    #             LiteralExpr(123)), 
    #         Token(TokenKind.STAR, '*', None, 1), 
    #         GroupingExpr(LiteralExpr(45.67)))
    # print(AstPrinter().print(expression))

    lang = Lang()
    if len(sys.argv) > 2:
        print("ERROR: USAGE 'main.py <source file>'")
        exit(69)
    elif len(sys.argv) == 2:
        source_file = sys.argv[1]
        lang.run_file(source_file)
    else:
        lang.run_prompt()

