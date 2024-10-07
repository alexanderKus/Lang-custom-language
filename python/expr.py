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
