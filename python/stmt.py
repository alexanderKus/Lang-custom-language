class Stmt:
    def accept(self, visitor):
        pass

class ClassStmt(Stmt):
    def __init__(self, name, super_class, methods):
        self.name = name
        self.super_class = super_class
        self.methods = methods

    def accept(self, visitor):
        return visitor.visit_class_stmt(self)

class FunctionStmt(Stmt):
    def __init__(self, name, function):
        self.name = name
        self.function = function

    def accept(self, visitor):
        return visitor.visit_function_stmt(self)

class ReturnStmt(Stmt):
    def __init__(self, keyword, value):
        self.keyword = keyword
        self.value = value

    def accept(self, visitor):
        return visitor.visit_return_stmt(self)

class WhileStmt(Stmt):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def accept(self, visitor):
        return visitor.visit_while_stmt(self)

class IfStmt(Stmt):
    def __init__(self, condition, then_branch, else_branch):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    def accept(self, visitor):
        return visitor.visit_if_stmt(self)

class BlockStmt(Stmt):
    def __init__(self, stmts):
        self.stmts = stmts

    def accept(self, visitor):
        return visitor.visit_block_stmt(self)

class VarStmt(Stmt):
    def __init__(self, name, initializer):
        self.name = name
        self.initializer = initializer

    def accept(self, visitor):
        return visitor.visit_var_stmt(self)

class ExpressionStmt(Stmt):
    def __init__(self, expr):
        self.expr = expr

    def accept(self, visitor):
        return visitor.visit_expression_stmt(self)

class PrintStmt(Stmt):
    def __init__(self, expr):
        self.expr = expr

    def accept(self, visitor):
        return visitor.visit_print_stmt(self)

class BreakStmt(Stmt):
    def __init__(self, name):
        self.name = name

    def accept(self, visitor):
        return visitor.visit_break_stmt(self)
