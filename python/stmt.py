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