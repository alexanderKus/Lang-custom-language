# LANG a custom language

- Two Implementations: Python and C (maybe rust in future).
- Has REPL.
- Dynamically typed.
- Hand-written GC (garbage collector) in C implementation.
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
primary      -> NUMBER | STRING | "true" | "false" | "nil"
                | "(" expression ")" ;
                | IDENTIFIER ;
                | functionBody;
arguments    -> expression ( "," expression )* ;
```

### EXAMPLES

```
coming soon...
```
