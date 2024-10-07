#!/usr/bin/python3

import sys
from common import ErrorHandler, RunTimeError
from lexer import Lexer
from parser import Parser
from interpreter import Interpreter


class Lang:
    def __init__(self):
        self.interpreter = Interpreter()
        self.eh = ErrorHandler(self)
        self.had_error = False
        self.had_runtime_error = False

    def run_prompt(self):
        while True:
            line = input('> ')
            if line != '' and line != None:
                self.run(line)
                self.had_error = False

    def run_file(self, source_file):
        source_code = ''
        try:
            with open(source_file, 'r') as f:
                source_code = f.read()
        except FileNotFoundError:
            self.eh.error(0, f'cannot open {source_file}')
            exit(68)
        self.run(source_code)
        if self.had_error:
            exit(69)
        if self.had_runtime_error:
            exit(70)

    def run(self, source_code):
        if source_code == 'exit()':
            exit(0)
        lexer = Lexer(source_code, self.eh)
        tokens = lexer.tokenize()
        parser = Parser(tokens, self.eh)
        stmts = parser.parse()
        if self.had_error:
            return
        # NOTE: sometimes stmts may contains None values,
        # skipping them may be a good idea, to run interpreter on valid statements
        try:
            gen = self.interpreter.interpret(stmts)
            for v in [g for g in gen if g is not None]:
                print(v)
        except RunTimeError as e:
            self.eh.runtime_error(e)

if __name__ == '__main__':
    lang = Lang()
    if len(sys.argv) > 2:
        print("ERROR: USAGE 'main.py <source file>'")
        exit(69)
    elif len(sys.argv) == 2:
        source_file = sys.argv[1]
        lang.run_file(source_file)
    else:
        lang.run_prompt()

