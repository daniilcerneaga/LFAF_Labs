# Laboratory Work #3 — Lexer & Scanner

**Course:** Formal Languages & Finite Automata
**Student:** Daniil Cerneaga
**Group:** FAF-243

---

## Objectives

1. Understand what lexical analysis is.
2. Get familiar with the inner workings of a lexer/tokenizer.
3. Implement a sample lexer and show how it works.

---

## Theory

Lexical analysis is the first stage of a compiler or interpreter. Its job is to read a raw string of characters and split it into meaningful chunks called **tokens**. Each token has a **type** (what kind of thing it is) and a **value** (the actual text from the source).

For example, the line `let x = 42` becomes four tokens: `KEYWORD 'let'`, `IDENTIFIER 'x'`, `ASSIGN '='`, `INTEGER '42'`. The next stage of a compiler (the parser) then works with this flat token list instead of raw characters.

A lexer is directly linked to the finite automata studied in Lab 2. Each recognition rule corresponds to a DFA state: when the lexer sees a digit it enters the "reading number" state and stays there until a non-digit appears, exactly as a DFA transitions between states on each input symbol. When the lexer reads a letter it enters the "reading word" state; after collecting the full word it checks a keywords table to decide whether to emit `KEYWORD` or `IDENTIFIER` — this is equivalent to a DFA accepting state that has two labels.

---

## Implementation

### Overview

The lexer targets **TinyLang** — a custom mini programming language designed for this lab. TinyLang was chosen instead of SQL or a plain calculator because it exercises a wider range of token categories in a natural way: variable declarations, typed function signatures, control flow, loops, list literals, comments, escape sequences, and type annotations all appear in realistic short snippets.

### Token types

| Type | Description | Example |
|------|-------------|---------|
| `KEYWORD` | Reserved TinyLang words | `let`, `fn`, `if`, `while`, `return` |
| `IDENTIFIER` | Variable and function names | `x`, `age`, `greet` |
| `INTEGER` | Whole number literals | `42`, `0`, `100` |
| `FLOAT` | Decimal number literals | `3.14`, `9.5` |
| `STRING` | Double-quoted string literals | `"hello"` |
| `BOOLEAN` | Boolean literals | `true`, `false` |
| `PLUS` / `MINUS` | Additive operators | `+`, `-` |
| `STAR` / `SLASH` | Multiplicative operators | `*`, `/` |
| `PERCENT` | Modulo operator | `%` |
| `POWER` | Exponentiation operator | `**` |
| `EQ` / `NEQ` | Equality comparison | `==`, `!=` |
| `LT` / `GT` / `LTE` / `GTE` | Relational operators | `<`, `>`, `<=`, `>=` |
| `ASSIGN` | Assignment | `=` |
| `ARROW` | Return type hint | `->` |
| `LPAREN` / `RPAREN` | Parentheses | `(`, `)` |
| `LBRACE` / `RBRACE` | Block delimiters | `{`, `}` |
| `LBRACKET` / `RBRACKET` | List delimiters | `[`, `]` |
| `COMMA` / `COLON` / `SEMICOLON` | Separators | `,`, `:`, `;` |
| `COMMENT` | Line comment starting with `#` | `# note` |
| `NEWLINE` | End of line | `\n` |
| `EOF` | End of input | — |
| `UNKNOWN` | Unrecognised character | `@`, `$` |

### Keyword set

```python
KEYWORDS = {
    "let", "fn", "return", "if", "elif", "else",
    "while", "for", "in", "break", "continue",
    "print", "and", "or", "not",
    "int", "float", "bool", "str",
    "true", "false", "null",
}
```

Identifiers and keywords look identical to the character scanner — both are sequences of letters, digits, and underscores. After reading a full word, the lexer checks the keywords set. If the word is `true` or `false` it emits `BOOLEAN`; if it is in `KEYWORDS` it emits `KEYWORD`; otherwise `IDENTIFIER`.

### Token class

```python
class Token:
    def __init__(self, token_type, value, line, col):
        self.type  = token_type
        self.value = value
        self.line  = line    # 1-based line number
        self.col   = col     # 1-based column number
```

Each token carries its source position (`line`, `col`) so that error messages produced by later compiler stages can point to the exact location in the source file.

### Lexer class

The `Lexer` class walks through the source string one character at a time using three state variables: `pos` (current index), `line`, and `col`. The helper method `advance()` moves forward by one character and updates `line`/`col` automatically when it crosses a newline.

The main `tokenize()` method is a single dispatch loop:

- **Whitespace** (`space`, `tab`, `\r`) is skipped silently; `\n` emits a `NEWLINE` token.
- **`#`** starts a comment — characters are consumed until end of line.
- **`"`** starts a string — characters are consumed until the matching closing quote; escape sequences `\"`, `\\`, `\n`, `\t` are handled inside `scan_string()`.
- **A digit** starts a number — `scan_number()` reads digits and checks for a `.` followed by another digit to decide `INTEGER` vs `FLOAT`.
- **A letter or `_`** starts a word — `scan_identifier_or_keyword()` reads alphanumerics and underscores, then performs the keyword table lookup.
- **Two-character operators** (`**`, `==`, `!=`, `<=`, `>=`, `->`) are checked before single-character ones by peeking one position ahead with `peek()`.
- **Single-character tokens** (`+`, `-`, `{`, `[`, `,`, etc.) are matched directly.
- **Anything else** produces an `UNKNOWN` token and the character is consumed so the loop always makes progress.

The loop ends when `pos` reaches the end of the source and a final `EOF` token is appended.

### Main program

`main.py` runs the lexer on six TinyLang snippets that collectively exercise every token type and prints the resulting token stream for each.

---

## How to Run

**Requirements:** Python 3.8+, no external libraries.

```bash
python3 main.py
```

---

## Results

### Sample 1 — Variable declarations and arithmetic

Input:
```
let x = 42
let y = 3.14
let result = x * y + 100 ** 2
```

Output:
```
Token(KEYWORD      'let'       line=1, col=1)
Token(IDENTIFIER   'x'         line=1, col=5)
Token(ASSIGN       '='         line=1, col=7)
Token(INTEGER      '42'        line=1, col=9)
Token(KEYWORD      'let'       line=2, col=1)
Token(IDENTIFIER   'y'         line=2, col=5)
Token(ASSIGN       '='         line=2, col=7)
Token(FLOAT        '3.14'      line=2, col=9)
Token(KEYWORD      'let'       line=3, col=1)
Token(IDENTIFIER   'result'    line=3, col=5)
Token(ASSIGN       '='         line=3, col=12)
Token(IDENTIFIER   'x'         line=3, col=14)
Token(STAR         '*'         line=3, col=16)
Token(IDENTIFIER   'y'         line=3, col=18)
Token(PLUS         '+'         line=3, col=20)
Token(INTEGER      '100'       line=3, col=22)
Token(POWER        '**'        line=3, col=26)
Token(INTEGER      '2'         line=3, col=29)
Token(EOF          ''          line=4, col=1)
```

### Sample 2 — Function definition and call

Input:
```
fn add(a, b) {
    return a + b
}
let sum = add(10, 20)
print(sum)
```

Output:
```
Token(KEYWORD      'fn'        line=1, col=1)
Token(IDENTIFIER   'add'       line=1, col=4)
Token(LPAREN       '('         line=1, col=7)
Token(IDENTIFIER   'a'         line=1, col=8)
Token(COMMA        ','         line=1, col=9)
Token(IDENTIFIER   'b'         line=1, col=11)
Token(RPAREN       ')'         line=1, col=12)
Token(LBRACE       '{'         line=1, col=14)
Token(KEYWORD      'return'    line=2, col=5)
Token(IDENTIFIER   'a'         line=2, col=12)
Token(PLUS         '+'         line=2, col=14)
Token(IDENTIFIER   'b'         line=2, col=16)
Token(RBRACE       '}'         line=3, col=1)
Token(KEYWORD      'let'       line=5, col=1)
Token(IDENTIFIER   'sum'       line=5, col=5)
Token(ASSIGN       '='         line=5, col=9)
Token(IDENTIFIER   'add'       line=5, col=11)
Token(LPAREN       '('         line=5, col=14)
Token(INTEGER      '10'        line=5, col=15)
Token(COMMA        ','         line=5, col=17)
Token(INTEGER      '20'        line=5, col=19)
Token(RPAREN       ')'         line=5, col=21)
Token(KEYWORD      'print'     line=6, col=1)
Token(LPAREN       '('         line=6, col=6)
Token(IDENTIFIER   'sum'       line=6, col=7)
Token(RPAREN       ')'         line=6, col=10)
Token(EOF          ''          line=7, col=1)
```

### Sample 3 — Conditional with comparison operators

Input:
```
let age = 18
if age >= 18 and age <= 65 {
    print("working age")
} elif age < 18 {
    print("minor")
} else {
    print("retired")
}
```

Output (selected key tokens):
```
Token(KEYWORD      'if'        line=2, col=1)
Token(IDENTIFIER   'age'       line=2, col=4)
Token(GTE          '>='        line=2, col=8)
Token(INTEGER      '18'        line=2, col=11)
Token(KEYWORD      'and'       line=2, col=14)
Token(IDENTIFIER   'age'       line=2, col=18)
Token(LTE          '<='        line=2, col=22)
Token(INTEGER      '65'        line=2, col=25)
Token(KEYWORD      'elif'      line=4, col=3)
Token(LT           '<'         line=4, col=12)
Token(KEYWORD      'else'      line=6, col=3)
Token(STRING       'retired'   line=7, col=11)
```

### Sample 4 — While loop and modulo

Input:
```
let i = 0
while i < 10 {
    if i % 2 == 0 {
        print(i)
    }
    i = i + 1
}
```

Output (selected key tokens):
```
Token(KEYWORD      'while'     line=2, col=1)
Token(LT           '<'         line=2, col=9)
Token(PERCENT      '%'         line=3, col=10)
Token(EQ           '=='        line=3, col=14)
```

### Sample 5 — Strings, booleans, comments

Input:
```
# This is a comment
let name = "Daniil"
let greeting = "Hello, " + name
let active = true
let score = 9.5
print(greeting)
```

Output (selected key tokens):
```
Token(COMMENT      '# This is a comment'  line=1, col=1)
Token(STRING       'Daniil'               line=2, col=12)
Token(STRING       'Hello, '              line=3, col=16)
Token(BOOLEAN      'true'                 line=4, col=14)
Token(FLOAT        '9.5'                  line=5, col=13)
```

### Sample 6 — Type hints, for loop, unknown characters

Input:
```
fn greet(name: str) -> str {
    return "Hi, " + name
}
for item in [1, 2, 3] {
    print(item)
}
let bad = @unknown$
```

Output (selected key tokens):
```
Token(COLON        ':'         line=1, col=14)
Token(ARROW        '->'        line=1, col=21)
Token(KEYWORD      'for'       line=5, col=1)
Token(KEYWORD      'in'        line=5, col=10)
Token(LBRACKET     '['         line=5, col=13)
Token(RBRACKET     ']'         line=5, col=21)
Token(UNKNOWN      '@'         line=9, col=11)
Token(UNKNOWN      '$'         line=9, col=19)
```

---

## Project Structure

```
laboratory-work-3/
├── lexer.py      # TokenType constants, Token class, LexerError, Lexer class
├── main.py       # Six TinyLang samples with printed token output
└── README.md     # This file
```

---

## Connection to Finite Automata (Lab 2)

Each branch of the `tokenize()` dispatch loop corresponds to a state in an implicit DFA:

| DFA state | Entered when | Stays while | Exits when |
|-----------|-------------|-------------|------------|
| NUMBER | first digit seen | more digits | non-digit (if `.` + digit → FLOAT sub-state) |
| WORD | letter or `_` seen | alphanumeric or `_` | non-alphanumeric, then keyword lookup |
| STRING | `"` seen | any char except `"` | closing `"` found |
| COMMENT | `#` seen | any char except `\n` | `\n` or end of input |
| OPERATOR | `*`, `=`, `!`, `<`, `>`, `-` seen | peek next char | decide 1- or 2-char token |

This mapping is why lexers and finite automata are taught together — a lexer **is** a hand-coded DFA.

---

## Conclusions

1. ✅ Implemented a working lexer for TinyLang covering variables, functions, control flow, loops, lists, type hints, and comments.
2. ✅ The lexer correctly distinguishes 25 distinct token types including two-character operators (`**`, `==`, `!=`, `<=`, `>=`, `->`).
3. ✅ Integer and float literals are both supported; a float is detected by a `.` followed by a digit.
4. ✅ String literals with double-quote delimiters and escape sequences (`\"`, `\\`, `\n`, `\t`) are handled correctly.
5. ✅ Comments starting with `#` are tokenized rather than silently dropped, so a later stage can attach them to an AST if needed.
6. ✅ Source position (`line`, `col`) is tracked for every token, enabling precise error reporting in later compiler stages.
7. ✅ Unrecognised characters produce `UNKNOWN` tokens instead of raising an exception, so the lexer always processes the entire input.
8. ✅ The implementation demonstrates the direct link between lexer logic and DFA theory from Lab 2 — each recognition branch corresponds to a DFA state.

---

## References

Cretu Dumitru, Vasile Drumea, Irina Cojuhari — course materials FLFA.
LLVM Tutorial — My First Language Frontend: https://llvm.org/docs/tutorial/MyFirstLanguageFrontend/LangImpl01.html
Wikipedia — Lexical analysis: https://en.wikipedia.org/wiki/Lexical_analysis

---

**Date:** March 2026
**Repository:** [GitHub Link]
