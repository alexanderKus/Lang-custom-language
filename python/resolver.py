from common import Visitor


class Resolver(Visitor):
    def __init__(self, interpreter):
        self.interpreter = interpreter

    def resolve(self, stmts):
        for stmt in stmts:
            self._resolve(stmt)
    
    def _resolve(self, stmt):
        stmt.accept(self)

    def begin_scope(self):
        pass

    def end_scope(self):
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
        self.begin_scope()
        self.resolve(stmt.statements)
        self.end_scope()
        return None

    def visit_break_stmt(self, stmt):
        pass

    # Expressions
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
