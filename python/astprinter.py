from common import Visitor
from tokens import Token
from expr import Expr, VariableExpr
from stmt import Stmt


class AstPrinter(Visitor):
    def visit_function_stmt(self, stmt):
        return f'(fun {stmt.name.lexeme} (' + \
          ' '.join([param.lexeme if param is stmt.function.params[0] else ' ' for param in stmt.function.params]) + \
          ') ' + \
          ' '.join([body.accept(self) for body in stmt.function.body]) + \
          ')'

    def visit_if_stmt(self, stmt):
        if stmt.else_branch is None:
            return self.parenthesize2('if', stmt.condition, stmt.then_branch)
        return self.parenthesize2('if-else', stmt.condition, stmt.then_branch, stmt.else_branch)

    def visit_var_stmt(self, stmt):
        if stmt.initializer is None:
            return self.parenthesize2('var', stmt.name)
        return self.parenthesize2('var', stmt.name, '=', stmt.initializer)

    def visit_expression_stmt(self, stmt):
        return self.parenthesize(';', stmt.expr)

    def visit_print_stmt(self, stmt):
        return self.parenthesize('print', stmt.expr)

    def visit_return_stmt(self, stmt):
        if stmt.value is None:
            return '(return)'
        return self.parenthesize('return', stmt.value)

    def visit_while_stmt(self, stmt):
        return self.parenthesize2('while', stmt.condition, stmt.body)

    def visit_block_stmt(self, stmt):
      return '(block' + ' '.join([s.accept(self) if s is not None else '' for s in stmt.stmts]) + ')'

    def visit_break_stmt(self, stmt):
        return '(break)'

    # Expressions
    def visit_function_expr(self, expr):
        return '(' + ' '.join(param.lexeme for param in expr.params) + ')'

    def visit_logical_expr(self, expr):
      return self.parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visit_call_expr(self, expr):
        return self.parenthesize2('call', expr.callee, *expr.arguments)

    def visit_variable_expr(self, expr):
        return str(expr.name.lexeme)

    def visit_assign_expr(self, expr):
        return self.parenthesize2('=', expr.name.lexeme, expr.value)

    def visit_binary_expr(self, expr):
        return self.parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visit_grouping_expr(self, expr):
        return self.parenthesize('group', expr.expression)

    def visit_literal_expr(self, expr):
        if expr.value is None:
            return 'nil'
        return str(expr.value)

    def visit_unary_expr(self, expr):
        return self.parenthesize(expr.operator.lexeme, expr.right)
    
    def printExpr(self, expr):
      return expr.accept(self)

    def printStmt(self, stmt):
      return stmt.accept(self)
    
    def parenthesize(self, name, *exprs):
        return f'({name} ' + ' '.join([e.accept(self) for e in exprs]) + ')'

    def parenthesize2(self, name, *parts):
        b =  f'({name}' 
        for part in parts:
            b += ' '
            if isinstance(part, Expr) or isinstance(part, Stmt):
                b += part.accept(self)
            elif isinstance(part, Token):
                b += part.lexeme
            else:
                b += str(part)
        b += ')'
        return b