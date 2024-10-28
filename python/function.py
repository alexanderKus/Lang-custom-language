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
    def __init__(self, name, declaration, closure, is_initializer):
        self.name = name
        self.declaration = declaration
        self.closure = closure
        self.is_initializer = is_initializer
    
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
            if self.is_initializer:
                return self.closure.get_at(0, 'this')
            return r.value
        if self.is_initializer:
            return self.closure.get_at(0, 'this')
        return None

    def arity(self):
        return len(self.declaration.params)

    def bind(self, instance):
        env = Environment(self.closure)
        env.define('this', instance)
        return LangFunction(self.name, self.declaration, env, self.is_initializer)