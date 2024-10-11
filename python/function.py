from common import Environment, Return

class LangCallable:
    def call(self, interpreter, arguments):
        pass

    def arity(self):
        pass

class Clock(LangCallable):
    def __str__(self):
        return '<native function>'

    def call(self, interpreter, arguments):
        import time
        return time.time()

    def arity(self):
        return 0

class LangFunction(LangCallable):
    def __init__(self, name, declaration, closure):
        self.name = name
        self.declaration = declaration
        self.closure = closure
    
    def __str__(self):
        if self.name is None:
            return '<fn>'
        return f'<fn {self.name}>'

    def call(self, interpreter, arguments):
        env = Environment(self.closure)
        for i in range(len(self.declaration.params)):
            env.define(self.declaration.params[i].lexeme, arguments[i])
        try:
            interpreter.execute_block(self.declaration.body, env)
        except Return as r:
            return r.value

    def arity(self):
        return len(self.declaration.params)
