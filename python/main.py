#!/usr/bin/python3

import sys
from enum import Enum

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
        self.had_error = False

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
        if self.had_error:
            exit(69)
        self.run(souce_code)

    def run(self, source_code):
        if source_code == 'exit()':
            exit(0)

        lexer = Lexer(source_code)
        tokens = lexer.tokenize()
        
        for token in tokens:
            print(token)

    def _error(line_number, message):
        self._report(line_number, '', message)

    def _report(line, where, message):
        ErrorHandler.report(line, where, massage)
        self.had_error = True

class ErrorHandler:
    @staticmethod
    def error(line_number, message):
        ErrorHandler.report(line_number, '', message)

    @staticmethod
    def report(line, where, message):
        # TODO: come up with better error handling
        print(f'[Line {line}] ERROR: {where} {message}')

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

