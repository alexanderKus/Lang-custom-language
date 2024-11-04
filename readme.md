# LANG a custom language

- Implemented with Python
- Has REPL.
- Dynamically typed.
- Build in data types: `boolean`, `number` (just IEEE-754), `string` and `nil`
- Supports classes

### USAGE

- To run REPL: `./lang.py`
- To from file: `./lang.py <file>`

### GRAMMAR

```
program      -> declaration* OEF ;
declaration  -> classDecl
                | funDecl
                | varDecl
                | statement ;
classDecl    -> "class" IDENTIFIER ( "<" IDENTIFIER )? "{" function* "}"
funDecl      -> "fun" function ;
function     -> IDENTIFIER functionBody;
functionBody -> "(" parameters? ")" block ;
parameters   -> IDENTIFIER ( "," IDENTIFIER )* ;
varDecl      -> "var" IDENTIFIER ( "=" expression )? ";" ;
statement    -> exprStmt
                | forStmt
                | ifStmt
                | printStmt
                | returnStmt
                | whileStmt
                | break
                | block ;
forStmt      -> "for" "(" ( varDecl | exprStmt| ";" )
                  expression? ";"
                  expression? ")" statement ;
exprStmt     -> expression ";" ;
ifStmt       -> "if" "(" expression ")" statement ( "else" statement )? ;
printStmt    -> "print" expression ";" ;
returnStmt   -> "return" expression? ";" ;
whileStmt    -> "while" "(" expression ")" statement ;
block        -> "{" declaration* "}" ;
expression   -> assignment ;
assignment   -> ( call "." )? IDENTIFIER "=" assignment
                | logic_or ;
logic_or     -> logic_and ( "or" logic_and )* ;
logic and    -> equality ( "and" equality )* ;
equality     -> comparison ( ( "!=" | "==" ) comparison )* ;
comparison   -> term ( ( ">" | ">=" | ">" | ">=" ) term )* ;
term         -> factor ( ( "-" | "+" ) factor )* ;
factor       -> unary ( ( "/" | "*" ) unary )* ;
unary        -> ( "!" | "-" ) unary
                | call ;
call         -> primary ( "(" arguments? ")" | "." IDENTIFIER)* ;
primary      -> NUMBER | STRING | IDENTIFIER | "true" | "false" | "nil" | "this
                | "(" expression ")" ;
                | "super" "." IDENTIFIER
                | functionBody;
arguments    -> expression ( "," expression )* ;
```

### EXAMPLES

Example #1

```
for(var i = 0; i < 10; i = i + 1) {
  print "Hello, World!";
  if (i == 2) break;
}
```

Result:

```
"Hello, World!"
"Hello, World!"
"Hello, World!"
```

Example #2

```
class Base {
  foo() {
    print "foo";
  }
}

class Square < Base {
  init(n) {
    this.n = n;
  }
  calc() {
    return this.n * 2;
  }
}

class Rectangle < Base {
  init(a, b) {
    this.a = a;
    this.b = b;
  }
  calc() {
    return this.a * this.b;
  }

  foo() {
    print "boo";
  }
}

var s = Square(10);
var r = Rectangle(25, 2);
print "Square: " + s.calc();
print "Rectangle: " + r.calc();
s.foo();
r.foo();
```

Result

```
Square: 20
Rectangle: 50

"foo"
"boo"
```
