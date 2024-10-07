from tokens import Token, TokenKind

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
