# Parser & Building an Abstract Syntax Tree

### Course: Formal Languages & Finite Automata
### Author: Daniil [Your Last Name]
### Group: [Your Group]
### Date: April 2026

---

## Theory

**Parsing** is the process of analysing a sequence of tokens to determine its grammatical structure according to a formal grammar. A parser typically consumes the token stream produced by a lexer and produces a tree structure that reflects the syntactic relationships in the source text.

An **Abstract Syntax Tree (AST)** is a hierarchical data structure that represents the logical structure of source code. Unlike a concrete parse tree, an AST omits syntactic noise (parentheses, semicolons, etc.) and keeps only the semantically meaningful nodes. Each node in the AST represents a construct — a declaration, an expression, a control-flow statement — and its children represent the sub-constructs it contains.

ASTs are widely used in compilers and interpreters: after parsing, subsequent phases (semantic analysis, type checking, code generation) all operate on the AST rather than on the raw token stream.

---

## Objectives

1. Get familiar with parsing and how it can be implemented programmatically.
2. Get familiar with the concept of an Abstract Syntax Tree.
3. Extend the lexer from Lab 3 with:
   - A `TokenType` class with regex-identifiable token categories (already present in `lexer.py`).
   - AST node data structures for the TinyLang grammar.
   - A recursive-descent parser that builds the AST from the token stream.

---

## Implementation

The implementation consists of three Python files:

### `lexer.py` (from Lab 3)

Defines `TokenType` (a class of string constants), `Token`, and `Lexer`. The lexer walks the source character-by-character and produces a flat list of `Token` objects. Every token carries its type, value, line, and column — information the parser uses for precise error messages.

### `ast_nodes.py` — AST Node Hierarchy

Every node inherits from `ASTNode`, which provides a `pretty()` method for printing the tree with indentation. Each subclass defines `_attrs()` (scalar fields) and `_children()` (child nodes / lists) so the base class can render them uniformly.

Nodes cover the full TinyLang grammar:

| Category       | Nodes |
|----------------|-------|
| Program        | `ProgramNode` |
| Statements     | `VarDeclNode`, `AssignNode`, `ReturnNode`, `PrintNode`, `BreakNode`, `ContinueNode`, `BlockNode` |
| Control flow   | `IfNode`, `WhileNode`, `ForNode` |
| Declarations   | `FunctionDefNode` |
| Expressions    | `BinaryOpNode`, `UnaryOpNode`, `FunctionCallNode`, `ListLiteralNode` |
| Literals       | `IntLiteralNode`, `FloatLiteralNode`, `StringLiteralNode`, `BoolLiteralNode`, `NullLiteralNode` |
| Names          | `IdentifierNode` |

### `parser.py` — Recursive-Descent Parser

The `Parser` class implements a classic **recursive-descent** parser. Each grammar rule maps directly to a Python method:

```
parse()                 → program
parse_statement()       → dispatch by current keyword/token
parse_var_decl()        → let IDENTIFIER = expression
parse_fn_def()          → fn IDENTIFIER ( params ) block
parse_if()              → if expr block [elif expr block]* [else block]?
parse_while()           → while expr block
parse_for()             → for IDENTIFIER in expr block
parse_block()           → { statement* }
parse_expression()      → top of expression hierarchy
parse_logical_or()      → logical_and ('or' logical_and)*
parse_logical_and()     → equality ('and' equality)*
parse_equality()        → comparison (('==' | '!=') comparison)*
parse_comparison()      → addition (('<'|'>'|'<='|'>=') addition)*
parse_addition()        → term (('+' | '-') term)*
parse_term()            → power (('*' | '/' | '%') power)*
parse_power()           → unary ('**' unary)*
parse_unary()           → ('not' | '-') unary | primary
parse_primary()         → literal | identifier | call | ( expr ) | [ list ]
```

Operator precedence is encoded naturally: lower-precedence operators are parsed higher in the call stack, so higher-precedence operations automatically bind tighter. For example, `x * y + 100 ** 2` produces:

```
BinaryOpNode  op='+'
  left:  BinaryOpNode op='*'  (x * y)
  right: BinaryOpNode op='**' (100 ** 2)
```

---

## Results

Running `main.py` produces the following ASTs for six sample programs.

### Sample 1 — Variable declarations and arithmetic

Source:
```
let x = 42
let y = 3.14
let result = x * y + 100 ** 2
```

AST (excerpt):
```
ProgramNode
  [statements]
    VarDeclNode  name='x'
      value:
        IntLiteralNode  value=42
    VarDeclNode  name='y'
      value:
        FloatLiteralNode  value=3.14
    VarDeclNode  name='result'
      value:
        BinaryOpNode  op='+'
          left:
            BinaryOpNode  op='*'
              left:  IdentifierNode  name='x'
              right: IdentifierNode  name='y'
          right:
            BinaryOpNode  op='**'
              left:  IntLiteralNode  value=100
              right: IntLiteralNode  value=2
```

### Sample 2 — Function definition and call

Source:
```
fn add(a, b) {
    return a + b
}
let sum = add(10, 20)
print(sum)
```

AST (excerpt):
```
FunctionDefNode  name='add'  params=['a', 'b']
  body:
    BlockNode
      [statements]
        ReturnNode
          value:
            BinaryOpNode  op='+'
              left:  IdentifierNode  name='a'
              right: IdentifierNode  name='b'
VarDeclNode  name='sum'
  value:
    FunctionCallNode  name='add'
      [args]
        IntLiteralNode  value=10
        IntLiteralNode  value=20
```

### Sample 3 — Conditional (if / elif / else)

The `IfNode` correctly captures the main condition, a list of elif clauses, and the else block. Compound boolean conditions like `age >= 18 and age <= 65` are represented as nested `BinaryOpNode` trees preserving operator precedence.

### Sample 4 — While loop with nested if

The `WhileNode` wraps a `BlockNode` that contains an `IfNode` and an `AssignNode`, demonstrating correct nesting of control-flow structures.

### Sample 5 — For loop with list literal

```
for item in [1, 2, 3] { print(item) }
```

Produces a `ForNode` whose `iterable` child is a `ListLiteralNode` containing three `IntLiteralNode` leaves.

### Sample 6 — Unary `not`, booleans, string concatenation

`UnaryOpNode` correctly wraps the `not` operator, and `BoolLiteralNode` stores Python `True`/`False` values converted from the TinyLang `true`/`false` tokens.

---

## Conclusions

In this laboratory work a recursive-descent parser was built on top of the existing TinyLang lexer. The main outcomes are:

- **Operator precedence** is handled cleanly through the layered grammar methods — no precedence table or Pratt parser needed for this grammar size.
- **AST node hierarchy** is extensible: adding a new construct requires only a new node class and a corresponding `parse_*` method.
- **Error reporting** is precise because every token carries line and column information that is propagated into `ParseError`.
- The `pretty()` method on `ASTNode` provides immediate visual feedback during development and is useful for debugging or for presenting the tree in reports.

---

## References

1. [Parsing — Wikipedia](https://en.wikipedia.org/wiki/Parsing)
2. [Abstract Syntax Tree — Wikipedia](https://en.wikipedia.org/wiki/Abstract_syntax_tree)
3. Aho, Lam, Sethi, Ullman — *Compilers: Principles, Techniques, and Tools* (Dragon Book), Chapter 4
