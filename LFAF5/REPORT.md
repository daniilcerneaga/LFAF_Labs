# Chomsky Normal Form — Laboratory Work 5

### Course: Formal Languages & Finite Automata
### Author: (your name)
### Variant: 6

---

## Theory

**Chomsky Normal Form (CNF)** is a restricted form of a context-free grammar where every production rule is of one of the following two forms:

- **A → BC** — a non-terminal produces exactly two non-terminals
- **A → a** — a non-terminal produces exactly one terminal

Additionally, the start symbol may produce the empty string (ε) if ε is in the language.

Every context-free language (except the empty language) can be represented by a CNF grammar. The conversion algorithm involves five steps:

1. **Eliminate ε-productions** — remove rules of the form A → ε (except possibly S → ε).
2. **Eliminate unit (renaming) productions** — remove rules of the form A → B.
3. **Eliminate inaccessible symbols** — remove non-terminals that cannot be reached from the start symbol.
4. **Eliminate non-productive symbols** — remove non-terminals that cannot derive any terminal string.
5. **Convert to binary form (CNF)** — replace terminals in long productions with dedicated non-terminals, and binarize productions of length ≥ 3.

---

## Variant 6 — Input Grammar

```
G = (VN, VT, P, S)
VN = {S, A, B, C, E}
VT = {a, b}

Productions P:
  1.  S → aB
  2.  S → AC
  3.  A → a
  4.  A → ASC
  5.  A → BC
  6.  B → b
  7.  B → bS
  8.  C → ε
  9.  C → BA
  10. E → bB
```

---

## Objectives

1. Understand Chomsky Normal Form and its significance.
2. Implement an algorithm to normalize a context-free grammar step by step.
3. Encapsulate the logic in a reusable class that accepts any grammar, not just Variant 6.

---

## Implementation

The implementation is in `cnf_converter.py` and consists of a `Grammar` class with methods for each normalization step, and a standalone `convert_to_cnf()` function that orchestrates the full pipeline.

### Class: `Grammar`

```python
class Grammar:
    def __init__(self, VN, VT, P, S): ...
    def eliminate_epsilon(self): ...
    def eliminate_unit_productions(self): ...
    def eliminate_inaccessible(self): ...
    def eliminate_nonproductive(self): ...
    def to_cnf(self): ...
```

The class accepts any grammar and performs each transformation in isolation, making the steps independently testable.

### Function: `convert_to_cnf(grammar, verbose=True)`

Orchestrates all five steps and optionally prints the grammar state after each step.

---

## Step-by-Step Conversion

### Step 1 — Eliminate ε-productions

**Nullable symbols found:** `{C}` (because `C → ε`)

Every production containing `C` gets a variant where `C` is omitted:
- `S → AC` gains variant `S → A`
- `A → ASC` gains variants `A → AS`, `A → AC` (→ later simplified), and `A → A`
- `A → BC` gains variant `A → B`

`C → ε` itself is removed.

**Grammar after Step 1:**
```
S → aB | AC | A
A → a | ASC | BC | AS | AC | B
B → b | bS
C → BA
E → bB
```

### Step 2 — Eliminate unit productions

Unit productions `S → A` and `A → B` are replaced by copying the target's rules into the source:

**Grammar after Step 2:**
```
S → aB | AC | a | ASC | BC | AS | b | bS
A → a | ASC | BC | AS | b | bS
B → b | bS
C → BA
E → bB
```

### Step 3 — Eliminate inaccessible symbols

Starting from `S`, we compute all reachable non-terminals.  
`E` is never reached from `S` → **removed**.

**Grammar after Step 3:**
```
VN = {S, A, B, C}
S → aB | AC | a | ASC | BC | AS | b | bS
A → a | ASC | BC | AS | b | bS
B → b | bS
C → BA
```

### Step 4 — Eliminate non-productive symbols

All non-terminals in the grammar (`S`, `A`, `B`, `C`) can derive terminal strings — none are removed.

### Step 5 — Convert to CNF

**Terminal wrapping:** Terminals appearing in productions of length ≥ 2 are replaced by wrapper non-terminals:
- `T_a` → `a`
- `T_b` → `b`

**Binarization:** Productions of length ≥ 3 are split into binary rules using auxiliary non-terminals:
- `A → ASC` becomes `A → A X1`, `X1 → SC`
- (similar for S)

**Final CNF Grammar:**
```
VN = {S, A, B, C, T_a, T_b, X1, X3}
VT = {a, b}
Start: S

Productions:
  S   → AC | T_a B | A X1 | AS | BC | a | b | T_b S
  A   → A X3 | AS | BC | T_b S | a | b
  B   → b | T_b S
  C   → BA
  T_a → a
  T_b → b
  X1  → SC
  X3  → SC
```

Every production is either `A → BC` or `A → a` — the grammar is in CNF. ✓

---

## Results

| Step | Action | Effect |
|------|--------|--------|
| 1 | Eliminate ε-productions | Removed `C → ε`, expanded affected rules; nullable = `{C}` |
| 2 | Eliminate unit productions | Removed `S → A`, `A → B`; rules copied over |
| 3 | Eliminate inaccessible symbols | Removed `E` |
| 4 | Eliminate non-productive symbols | None found |
| 5 | CNF binarization | Added `T_a`, `T_b`, `X1`, `X3`; all rules binary |

---

## Conclusions

In this lab I implemented a complete CNF conversion algorithm for context-free grammars. The algorithm correctly handles all five normalization steps in the required order. The implementation is generic — it accepts any CFG represented as a `Grammar` object, not just the Variant 6 grammar. This was verified with a custom demo grammar shown at the end of the script output.

The key insight is that steps must be performed in order: removing ε-productions before unit productions, and eliminating inaccessible/non-productive symbols before the final CNF binarization, to avoid reintroducing eliminated constructs.

---

## References

1. [Chomsky Normal Form — Wikipedia](https://en.wikipedia.org/wiki/Chomsky_normal_form)
2. Sipser, M. — *Introduction to the Theory of Computation*, Chapter 2.
