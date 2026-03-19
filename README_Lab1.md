# Laboratory Work #1 - Formal Languages and Finite Automata

**Course:** Formal Languages & Finite Automata  
**Variant:** 5  
**Student:** Cretu Dumitru  
**Group:** FAF-2XX

---

## Objectives

1. Understand formal language components (alphabet, grammar, productions)
2. Implement a Grammar class that generates valid strings
3. Convert Grammar to Finite Automaton
4. Implement string validation using the Finite Automaton

---

## Grammar Specification

**Variant 5:**

```
VN = {S, F, L}          // Non-terminal symbols
VT = {a, b, c, d}       // Terminal symbols
S = S                   // Start symbol

Production Rules (P):
    S → bS              // Can repeat 'b' at start
    S → aF              // Transition to state F
    S → d               // Terminal production
    F → cF              // Can repeat 'c'
    F → dF              // Can repeat 'd'
    F → aL              // Transition to state L
    F → b               // Terminal production
    L → aL              // Can repeat 'a'
    L → c               // Terminal production
```

This is a **right-linear regular grammar** (Type 3 in Chomsky hierarchy).

---

## Implementation

### 1. Grammar Class (`grammar.py`)

**Features:**
- Stores grammar components (VN, VT, P, S)
- `generate_string()` - Randomly generates valid strings by applying production rules
- `to_finite_automaton()` - Converts grammar to equivalent FA

**Algorithm for string generation:**
1. Start with symbol S
2. Randomly select applicable production rule
3. Apply rule: append the terminal, move to the next non-terminal (if any)
4. Repeat until only terminals remain

### 2. Finite Automaton Class (`grammar.py`)

**Features:**
- Stores FA components (Q, Σ, δ, q₀, F)
- `string_belongs_to_language()` - Validates if string is accepted

**Algorithm for validation:**
1. Start from initial state q₀ with a set of current states
2. For each symbol, compute the set of reachable next states
3. Accept if any current state is a final state after reading the full string

### 3. Main Program (`main.py`)

Demonstrates all functionality:
- Creates Grammar instance for Variant 5
- Generates 5 example strings
- Converts Grammar → FA
- Tests validation on multiple test strings (both valid and invalid)

---

## How to Run

**Requirements:** Python 3.8+

```bash
# Run the program
python3 main.py
```

**Expected Output:**
1. Grammar structure display
2. 5 generated valid strings
3. Finite Automaton structure (states, transitions)
4. Validation results for test strings

---

## Results

### Generated Strings Examples

```
1. d
2. ab
3. adccb
4. baccac
5. bbab
```

### Automaton Structure

**States (Q):** {S, F, L, FINAL}  
**Alphabet (Σ):** {a, b, c, d}  
**Initial State (q₀):** S  
**Final States (F):** {FINAL}

**Transition Function (δ):**

| State     | a     | b     | c     | d     |
|-----------|-------|-------|-------|-------|
| S (start) | F     | S     | -     | FINAL✓|
| F         | L     | FINAL✓| F     | F     |
| L         | L     | -     | FINAL✓| -     |

FINAL✓ = transition to final/accepting state

### String Validation Examples

**Accepted strings:**
- `d` ✓ — Path: S →(d) FINAL
- `ab` ✓ — Path: S →(a) F →(b) FINAL
- `aac` ✓ — Path: S →(a) F →(a) L →(c) FINAL
- `acb` ✓ — Path: S →(a) F →(c) F →(b) FINAL
- `bbd` ✓ — Path: S →(b) S →(b) S →(d) FINAL
- `bbab` ✓ — Path: S →(b) S →(b) S →(a) F →(b) FINAL

**Rejected strings:**
- `""` ✗ — Empty string, no transition possible from S
- `a` ✗ — S →(a) F, but F is not a final state
- `ba` ✗ — S →(b) S →(a) F, but F is not a final state
- `bc` ✗ — S →(b) S, no transition from S on 'c'
- `ca` ✗ — No transition from S on 'c'

---

## Project Structure

```
laboratory-work-1/
├── grammar.py              # Grammar and FiniteAutomaton class implementations
├── main.py                 # Main execution script
├── README.md               # This file
```

---

## Language Properties

**Accepted String Patterns:**

1. `b*d` — Any number of 'b's followed by 'd'
   - Examples: `d`, `bd`, `bbd`

2. `b*a(c|d)*b` — 'b's, then 'a', any mix of 'c'/'d', ending with 'b'
   - Examples: `ab`, `acb`, `addb`, `bacb`, `bbadcb`

3. `b*a(c|d)*a+c` — 'b's, 'a', mix of 'c'/'d', one or more 'a's, ending with 'c'
   - Examples: `aac`, `adac`, `baaac`, `baddaac`

**Minimal String:** `d` (length = 1)

**Key Characteristics:**
- Must start with 'b', 'a', or 'd'
- Must end with 'b', 'c', or 'd' (only terminal productions)
- Regular language (can be recognized by a finite automaton)

---

## Conversion Process: Grammar → FA

**Conversion Rules:**
1. Each non-terminal becomes a state
2. Add one final state FINAL
3. For rule `A → aB`: create transition δ(A, a) = B
4. For rule `A → a`: create transition δ(A, a) = FINAL

**Example:**
- Production `S → bS` becomes δ(S, b) = S (self-loop)
- Production `S → d` becomes δ(S, d) = FINAL (to final state)
- Production `F → aL` becomes δ(F, a) = L
- Production `L → c` becomes δ(L, c) = FINAL (to final state)

---

## Conclusions

1. ✅ Successfully implemented Grammar class for Variant 5
2. ✅ String generation algorithm works correctly with recursive and terminal productions
3. ✅ Grammar to FA conversion follows standard right-linear grammar rules
4. ✅ Finite Automaton correctly validates all test strings using NFA simulation
5. ✅ Demonstrated equivalence between regular grammar and finite automaton

**Key Learning:**
- Regular grammars can be mechanically converted to finite automata
- Both representations describe the same language
- NFA simulation with a set of current states handles non-determinism correctly (O(n·|Q|) time complexity)

---

## References

- Course materials: "Formal Languages & Finite Automata" by Cretu Dumitru
- Hopcroft, J. E., et al. (2006). *Introduction to Automata Theory, Languages, and Computation*

---

**Date:** February 2026  
**Repository:** [GitHub Link]
