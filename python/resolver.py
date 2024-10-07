from common import Visitor


class Resolver(Visitor):
    def __init__(self, interpreter):
        self.interpreter = interpreter
    
    def visit_block_stmt(self, stmt):
        self.begin_scope()
        self.resolve(stmt.statements)
        self.end_scope()
        return None

    def begin_scope(self):
        pass

    def resolve(self, stmts):
        for stmt in stmts:
            self._resolve(stmt)
    
    def _resolve(self, stmt):
        stmt.accept(self)

    def end_scope(self):
        pass