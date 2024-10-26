from function import LangCallable
from common import RunTimeError

class LangClass(LangCallable):
    def __init__(self, name, methods):
        self.name = name
        self.methods = methods

    def __str__(self):
        return self.name
  
    def call(self, interpreter, arguments):
        instance = LangInstance(self)
        return instance
    
    def find_method(self, name):
        return self.methods.get(name)

    def arity(self):
        return 0

class LangInstance:
    def __init__(self, klass):
        self.klass = klass
        self.fields = {}
      
    def __str__(self):
        return f'{self.klass} instance'
    
    def get(self, name):
        if name.lexeme in self.fields:
            return self.fields.get(name.lexeme)
        method = self.klass.find_method(name.lexeme)
        if method is not None:
            return method.bind(self)
        raise RunTimeError(name, f'Undefined property {name.lexeme}')

    def set(self, name, value):
        self.fields[name.lexeme] = value
