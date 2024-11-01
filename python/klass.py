from function import LangCallable
from common import RunTimeError

class LangClass(LangCallable):
    def __init__(self, name, super_class, methods):
        self.name = name
        self.super_class = super_class
        self.methods = methods

    def __str__(self):
        return self.name
  
    def call(self, interpreter, arguments):
        instance = LangInstance(self)
        initializer = self.find_method('init')
        if initializer is not None:
            initializer.bind(instance).call(interpreter, arguments)
        return instance
    
    def find_method(self, name):
        if name in self.methods:
            return self.methods.get(name)
        if self.super_class is not None:
            return self.super_class.find_method(name)
        return None

    def arity(self):
        initializer = self.find_method('init')
        if initializer is None:
            return 0
        return initializer.arity()

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
