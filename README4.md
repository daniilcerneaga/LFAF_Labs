# Laboratory Work #4 — Regular Expressions

**Course:** Formal Languages & Finite Automata  
**Variant:** 2  
**Student:** Daniil Cerneaga  
**Group:** FAF-243  

---

## Objectives

1. Understand what regular expressions are and what they are used for.
2. Write a program that **dynamically** interprets a given regular expression and generates valid strings that conform to it — the generator must not hardcode any specific pattern.
3. Cap unbounded quantifiers (`*`, `+`) at a maximum of 5 repetitions to avoid generating extremely long strings.
4. **Bonus:** Implement a step-by-step processing trace that records every decision made during string generation.

---

## Theory — What Are Regular Expressions?

A **regular expression** (regex) is a formal notation for describing a set of strings, i.e. a regular language. It is defined recursively:

| Construct | Meaning |
|-----------|---------|
| `a` | The literal character `a` |
| `AB` | Concatenation: `A` followed by `B` |
| `A\|B` | Alternation: either `A` or `B` |
| `A?` | Optional: zero or one occurrence of `A` |
| `A*` | Kleene star: zero or more occurrences |
| `A+` | One or more occurrences |
| `A{n}` | Exactly `n` occurrences |
| `A{n,m}` | Between `n` and `m` occurrences |
| `(A)` | Grouping: treat `A` as a unit |

Regular expressions are equivalent in expressive power to **finite automata** — every regex can be converted to an NFA (Thompson's construction) and vice versa. In practice they are used for input validation, lexical analysis (tokenisers/lexers), search-and-replace tools, and data extraction.

---

## Variant 2 — Patterns

The three regular expressions assigned for Variant 2 are:

| # | Pattern | Informal description |
|---|---------|----------------------|
| 1 | `M?N²(O\|P)³Q*R*` | Optional M, exactly two N's, three choices of O or P, any number of Q's, any number of R's |
| 2 | `(X\|Y\|Z)³8*(9\|0)*` | Three characters from {X,Y,Z}, any number of 8's, any number of digits 9 or 0 |
| 3 | `(H\|I)(J\|K)L*N?` | One of H/I, one of J/K, any number of L's, optional N |

In the code the superscripts are written as `{n}` quantifiers and `²` is treated as `{2}`, so the patterns passed to the parser are:

```
M?N{2}(O|P){3}Q*R*
(X|Y|Z){3}8*(9|0)*
(H|I)(J|K)L*N?
```

---

## Implementation

### Architecture Overview

The program is split into three logical layers:

```
regex string
    │
    ▼
┌─────────────┐
│ RegexParser │  Tokenises the pattern and builds an Abstract Syntax Tree (AST)
└──────┬──────┘
       │  AST
       ▼
┌───────────────┐
│ RegexGenerator│  Traverses the AST, making random choices at each decision point,
│               │  and records every step to produce a processing trace
└──────┬────────┘
       │  (string, trace)
       ▼
    Output
```

### 1. AST Node Classes

Four dataclasses represent all constructs a regex can contain:

```python
@dataclass
class Literal:
    char: str           # a single character, e.g. 'M'

@dataclass
class Concat:
    children: List[Any] # ordered sequence of nodes

@dataclass
class Alternation:
    options: List[Any]  # one branch is chosen at generation time

@dataclass
class Repeat:
    child: Any
    min_rep: int        # minimum number of repetitions
    max_rep: int        # maximum number of repetitions (capped at 5 for * and +)
```

These four types are sufficient to represent any regex built from the constructs listed in the theory section.

### 2. `RegexParser` — Recursive-Descent Parser

`RegexParser` converts a pattern string into an AST using recursive descent. The grammar it recognises is:

```
expr       ::= concat ( '|' concat )*
concat     ::= quantified+
quantified ::= atom quantifier?
atom       ::= '(' expr ')' | literal
quantifier ::= '?' | '*' | '+' | '{' n '}' | '{' n ',' m '}'
```

Key methods:

| Method | Role |
|--------|------|
| `parse()` | Entry point; resets position and calls `_parse_expr()` |
| `_parse_expr()` | Handles alternation; collects branches separated by `\|` |
| `_parse_concat()` | Handles concatenation; loops until `\|` or `)` is seen |
| `_parse_atom()` | Reads one group `(...)` or one literal character |
| `_apply_quantifier()` | Wraps the preceding atom in a `Repeat` node |
| `_parse_brace()` | Parses `{n}` and `{n,m}` quantifiers |

`*` and `+` are immediately translated to `Repeat(0, MAX_REPEAT)` and `Repeat(1, MAX_REPEAT)` respectively, where `MAX_REPEAT = 5`.

### 3. `RegexGenerator` — Random String Generator with Trace

`RegexGenerator.generate(ast)` performs a depth-first traversal of the AST and returns a generated string together with a list of trace steps.

Behaviour at each node type:

| Node | Action |
|------|--------|
| `Literal` | Appends the character to the result; logs `Emit 'X'` |
| `Concat` | Recursively generates all children in order; logs the count |
| `Alternation` | Picks one branch at random (`random.randrange`); logs which alternative was chosen |
| `Repeat` | Picks a count in `[min_rep, max_rep]` at random; logs the range and chosen count, then loops |

Indentation in the trace grows with recursion depth so the output visually mirrors the tree structure.

### 4. `print_ast()` — AST Visualiser

A standalone recursive function that pretty-prints the parsed AST before generation, giving a clear view of how the pattern was understood:

```
Concat:
  Repeat(0..1):
    Literal('M')
  Repeat(2):
    Literal('N')
  Repeat(3):
    Alternation:
      Literal('O')
      Literal('P')
  Repeat(0..5):
    Literal('Q')
  Repeat(0..5):
    Literal('R')
```

---

## Results

### Pattern 1 — `M?N{2}(O|P){3}Q*R*`

**AST:**
```
Concat:
  Repeat(0..1):
    Literal('M')
  Repeat(2):
    Literal('N')
  Repeat(3):
    Alternation:
      Literal('O')
      Literal('P')
  Repeat(0..5):
    Literal('Q')
  Repeat(0..5):
    Literal('R')
```

**Sample generated strings:**

| Example | Output |
|---------|--------|
| 1 | `NNOOOQ` |
| 2 | `NNPPPQQRRRRR` |
| 3 | `MNNOOOQQQRRRR` |
| 4 | `NNPOPQQQQRRR` |
| 5 | `MNNPPPQR` |

All strings satisfy:
- `M` appears 0 or 1 times at the start
- `NN` always present (exactly 2)
- Exactly 3 characters each being `O` or `P`
- 0–5 `Q`'s followed by 0–5 `R`'s

---

### Pattern 2 — `(X|Y|Z){3}8*(9|0)*`

**AST:**
```
Concat:
  Repeat(3):
    Alternation:
      Literal('X')
      Literal('Y')
      Literal('Z')
  Repeat(0..5):
    Literal('8')
  Repeat(0..5):
    Alternation:
      Literal('9')
      Literal('0')
```

**Sample generated strings:**

| Example | Output |
|---------|--------|
| 1 | `YXX888900` |
| 2 | `ZYZ888990` |
| 3 | `ZXZ888889` |
| 4 | `ZZZ800099` |
| 5 | `XYZ888800` |

All strings satisfy:
- Exactly 3 characters from {X, Y, Z}
- 0–5 eights
- 0–5 digits from {9, 0}

---

### Pattern 3 — `(H|I)(J|K)L*N?`

**AST:**
```
Concat:
  Alternation:
    Literal('H')
    Literal('I')
  Alternation:
    Literal('J')
    Literal('K')
  Repeat(0..5):
    Literal('L')
  Repeat(0..1):
    Literal('N')
```

**Sample generated strings:**

| Example | Output |
|---------|--------|
| 1 | `HKLLLN` |
| 2 | `HJLLLN` |
| 3 | `IJL` |
| 4 | `IJLLL` |
| 5 | `IJLN` |

All strings satisfy:
- One of H or I
- One of J or K
- 0–5 L's
- Optional N at the end

---

## Bonus — Processing Trace

The `RegexGenerator` records every decision made during string construction. Below is the full trace for Pattern 1, Example 1 (output: `NNOOOQ`):

```
Concatenate 5 part(s):
  Repeat 0× (allowed range: 0–1):          ← M is skipped
  Repeat 2× (allowed range: 2–2):
    Iteration 1/2:
      Emit 'N'
    Iteration 2/2:
      Emit 'N'
  Repeat 3× (allowed range: 3–3):
    Iteration 1/3:
      Choose alternative 1 of 2             ← O chosen
        Emit 'O'
    Iteration 2/3:
      Choose alternative 1 of 2             ← O chosen
        Emit 'O'
    Iteration 3/3:
      Choose alternative 1 of 2             ← O chosen
        Emit 'O'
  Repeat 1× (allowed range: 0–5):
    Emit 'Q'
  Repeat 0× (allowed range: 0–5):          ← R section skipped
```

The trace reads exactly like a recipe: each node type announces what it is doing, alternation nodes report which branch they selected, and repeat nodes state both the chosen count and the allowed range. This makes it straightforward to audit that every generated string is genuinely valid under the pattern.

---

## Project Structure

```
laboratory-work-4/
└── regex_generator.py   # All classes and driver code in one file
└── task.md              # Original task description
└── README4.md           # This report
```

---

## How to Run

**Requirements:** Python 3.8+, no external libraries needed.

```bash
python regex_generator.py
```

The program will print, for each of the 3 patterns:
1. The pattern string
2. Its Abstract Syntax Tree
3. Five randomly generated valid strings, each accompanied by its full processing trace

To use the generator programmatically with custom patterns:

```python
from regex_generator import RegexParser, RegexGenerator

parser    = RegexParser("(A|B){2}C*")
ast       = parser.parse()
generator = RegexGenerator()
string    = generator.generate(ast)

print(string)                          # e.g. "ABCC"
print("\n".join(generator.steps))      # full trace
```

---

## Difficulties and Observations

**Operator precedence in the parser.** In a naive implementation it is tempting to handle alternation and concatenation at the same recursive level. Separating them into `_parse_expr` (alternation, lowest precedence) and `_parse_concat` (concatenation, higher precedence) was necessary so that `AB|CD` correctly parses as `(AB)|(CD)` rather than `A(B|C)D`.

**Brace quantifiers `{n}` vs. superscript notation.** The lab sheet uses typographic superscripts (N², (O|P)³). These had to be translated to brace form (`{2}`, `{3}`) before being fed to the parser since the parser operates on plain ASCII strings. This is a natural limitation for any tool working with keyboard-typeable regex syntax.

**Capping unbounded quantifiers.** The `*` and `+` operators denote potentially infinite repetition. Setting `MAX_REPEAT = 5` at the `Repeat` node construction point — rather than during generation — keeps the constraint centralised and easy to change.

**Trace depth tracking.** Making the trace readable required careful management of a `_depth` counter that increases on each recursive call. Without this, the nested structure of traces for deeply grouped expressions would be indistinguishable.

---

## Conclusion

The lab demonstrated how a formal grammar can be used to build a recursive-descent parser that converts a human-readable regular expression into a structured AST. The AST then serves as a blueprint for a generator that makes random valid choices at each branching point. The approach is fully dynamic: no part of the code is specific to Variant 2's three patterns — any regex composed of literals, groups, alternation, and quantifiers can be passed as input and valid strings will be produced. The bonus trace feature makes the internal logic fully transparent and is directly useful for debugging or explaining the semantics of a pattern to a learner.
