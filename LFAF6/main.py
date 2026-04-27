"""
main.py — Demonstrates the full Lexer → Parser → AST pipeline for TinyLang.

Run:
    python main.py
"""

from lexer  import Lexer
from parser import Parser


# ------------------------------------------------------------------ #
#  Helper                                                              #
# ------------------------------------------------------------------ #

def run(title: str, source: str):
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")
    print("Source:")
    for line in source.strip().splitlines():
        print(f"    {line}")

    lexer  = Lexer(source)
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    try:
        ast = parser.parse()
        print("\nAST:")
        print(ast.pretty())
    except Exception as e:
        print(f"\n  [ERROR] {e}")


# ------------------------------------------------------------------ #
#  Sample 1 — Variable declarations and arithmetic                    #
# ------------------------------------------------------------------ #
run("Sample 1 — Variable declarations and arithmetic", """\
let x = 42
let y = 3.14
let result = x * y + 100 ** 2
""")


# ------------------------------------------------------------------ #
#  Sample 2 — Function definition and call                            #
# ------------------------------------------------------------------ #
run("Sample 2 — Function definition and call", """\
fn add(a, b) {
    return a + b
}

let sum = add(10, 20)
print(sum)
""")


# ------------------------------------------------------------------ #
#  Sample 3 — Conditional with comparison operators                   #
# ------------------------------------------------------------------ #
run("Sample 3 — Conditional with comparison operators", """\
let age = 18
if age >= 18 and age <= 65 {
    print("working age")
} elif age < 18 {
    print("minor")
} else {
    print("retired")
}
""")


# ------------------------------------------------------------------ #
#  Sample 4 — While loop and modulo                                   #
# ------------------------------------------------------------------ #
run("Sample 4 — While loop and modulo", """\
let i = 0
while i < 10 {
    if i % 2 == 0 {
        print(i)
    }
    i = i + 1
}
""")


# ------------------------------------------------------------------ #
#  Sample 5 — For loop over a list                                    #
# ------------------------------------------------------------------ #
run("Sample 5 — For loop over list literal", """\
for item in [1, 2, 3] {
    print(item)
}
""")


# ------------------------------------------------------------------ #
#  Sample 6 — Strings, booleans, unary not                           #
# ------------------------------------------------------------------ #
run("Sample 6 — Strings, booleans, unary not", """\
let name = "Daniil"
let active = true
let inactive = not active
let greeting = "Hello, " + name
print(greeting)
""")
