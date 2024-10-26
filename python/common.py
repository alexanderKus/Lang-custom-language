from tokens import TokenKind

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
    
    def warningT(self, token, message):
        print(f'[WARNING: {token.line}] `{token.lexeme}` {message}')

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
    
    def get_at(self, distance, name):
        return self.ancestor(distance).values[name]

    def assign(self, token, value):
        if token.lexeme in self.values:
            self.values[token.lexeme] = value
            return
        if self.enclosing is not None:
            self.enclosing.assign(token, value)
            return
        raise RunTimeError(token, f'Undefined variable "{token.lexeme}"')
    
    def assign_at(self, distance, name, value):
        self.ancestor(distance).values[name.lexeme] = value

    def ancestor(self, distance):
        env = self
        for i in range(distance):
            env = env.enclosing
        return env


# TODO: instead of pass raise NotImplemented exception
class Visitor:
    # Statements
    def visit_class_stmt(self, stmt):
        pass

    def visit_function_stmt(self, stmt):
        pass

    def visit_if_stmt(self, stmt):
        pass

    def visit_var_stmt(self, stmt):
        pass

    def visit_expression_stmt(self, stmt):
        pass

    def visit_print_stmt(self, stmt):
        pass

    def visit_return_stmt(self, stmt):
        pass

    def visit_while_stmt(self, stmt):
        pass

    def visit_block_stmt(self, stmt):
        pass

    def visit_break_stmt(self, stmt):
        pass

    # Expressions
    def visit_this_expr(self, expr):
        pass

    def visit_get_expr(self, expr):
        pass

    def visit_set_expr(self, expr):
        pass

    def visit_function_expr(self, expr):
        pass
    
    def visit_logical_expr(self, expr):
        pass

    def visit_call_expr(self, expr):
        pass

    def visit_variable_expr(self, expr):
        pass

    def visit_assign_expr(self, expr):
        pass

    def visit_binary_expr(self, expr):
        pass

    def visit_grouping_expr(self, expr):
        pass

    def visit_literal_expr(self, expr):
        pass

    def visit_unary_expr(self, expr):
        pass
