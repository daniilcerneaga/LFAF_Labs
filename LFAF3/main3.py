from lexer import Lexer, TokenType


def run(title: str, source: str, skip_newlines: bool = True):
    """Tokenize source and print the token stream."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")
    print("Source:")
    print(source)
    print("\nTokens:")

    lexer  = Lexer(source)
    tokens = lexer.tokenize()

    for tok in tokens:
        if skip_newlines and tok.type == TokenType.NEWLINE:
            continue
        print(f"  {tok}")


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
#  Sample 5 — Strings, booleans, comments, escape sequences          #
# ------------------------------------------------------------------ #
run("Sample 5 — Strings, booleans, comments", """\
# This is a comment
let name = "Daniil"
let greeting = "Hello, " + name
let active = true
let score = 9.5
print(greeting)
""")


# ------------------------------------------------------------------ #
#  Sample 6 — For loop, arrow (return type hint), unknown chars       #
# ------------------------------------------------------------------ #
run("Sample 6 — For loop, type hints, unknown chars", """\
fn greet(name: str) -> str {
    return "Hi, " + name
}

for item in [1, 2, 3] {
    print(item)
}

let bad = @unknown$
""")
