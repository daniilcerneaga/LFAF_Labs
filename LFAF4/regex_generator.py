#!/usr/bin/env python3
"""
Lab 4 – Regular Expressions
Course: Formal Languages & Finite Automata
Variant 2

Patterns:
  1. M?N{2}(O|P){3}Q*R*
  2. (X|Y|Z){3}8*(9|0)*
  3. (H|I)(J|K)L*N?

The program dynamically parses any regex built from:
  - Literals
  - Grouping: (...)
  - Alternation: A|B
  - Quantifiers: ?, *, +, {n}, {n,m}

* and + are capped at MAX_REPEAT (default 5) as required by the task.
"""

import random
from dataclasses import dataclass, field
from typing import List, Optional, Any

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

MAX_REPEAT = 5          # cap for * and + quantifiers
EXAMPLES_PER_PATTERN = 5


# ---------------------------------------------------------------------------
# AST Node definitions
# ---------------------------------------------------------------------------

@dataclass
class Literal:
    """A single character."""
    char: str

    def describe(self) -> str:
        return f"Literal('{self.char}')"


@dataclass
class Concat:
    """Concatenation of multiple nodes."""
    children: List[Any]

    def describe(self) -> str:
        return f"Concat[{len(self.children)}]"


@dataclass
class Alternation:
    """One choice from several options  (A | B | C)."""
    options: List[Any]

    def describe(self) -> str:
        return f"Alternation[{len(self.options)} options]"


@dataclass
class Repeat:
    """Repeat a node between min_rep and max_rep times."""
    child: Any
    min_rep: int
    max_rep: int

    def describe(self) -> str:
        lo, hi = self.min_rep, self.max_rep
        if lo == hi:
            return f"Repeat(exactly {lo})"
        return f"Repeat({lo}..{hi})"


# ---------------------------------------------------------------------------
# Parser: regex string  →  AST
# ---------------------------------------------------------------------------

class RegexParser:
    """
    Recursive-descent parser that handles:
      Literals, groups ( ), alternation |, quantifiers ? * + {n} {n,m}
    """

    def __init__(self, pattern: str, max_repeat: int = MAX_REPEAT):
        self.pattern = pattern
        self.pos = 0
        self.max_repeat = max_repeat

    # ── public entry point ──────────────────────────────────────────────────

    def parse(self) -> Any:
        self.pos = 0
        node = self._parse_expr()
        return node

    # ── grammar rules ───────────────────────────────────────────────────────

    def _parse_expr(self) -> Any:
        """expr  ::=  quantified (  '|' quantified  )*"""
        left = self._parse_concat()
        if self.pos < len(self.pattern) and self.pattern[self.pos] == '|':
            options = [left]
            while self.pos < len(self.pattern) and self.pattern[self.pos] == '|':
                self.pos += 1          # consume '|'
                options.append(self._parse_concat())
            return Alternation(options)
        return left

    def _parse_concat(self) -> Any:
        """concat  ::=  quantified+  (stops at '|' or ')')"""
        children = []
        while self.pos < len(self.pattern) and self.pattern[self.pos] not in '|)':
            node = self._parse_quantified()
            if node is not None:
                children.append(node)
        if not children:
            return Literal('')
        if len(children) == 1:
            return children[0]
        return Concat(children)

    def _parse_quantified(self) -> Optional[Any]:
        """quantified  ::=  atom  quantifier?"""
        atom = self._parse_atom()
        if atom is None:
            return None
        return self._apply_quantifier(atom)

    def _parse_atom(self) -> Optional[Any]:
        """atom  ::=  '(' expr ')' | literal"""
        if self.pos >= len(self.pattern):
            return None
        c = self.pattern[self.pos]
        if c == '(':
            return self._parse_group()
        if c not in '*+?{|)':
            self.pos += 1
            return Literal(c)
        return None

    def _parse_group(self) -> Any:
        """group  ::=  '(' expr ')'"""
        self.pos += 1          # consume '('
        node = self._parse_expr()
        if self.pos < len(self.pattern) and self.pattern[self.pos] == ')':
            self.pos += 1      # consume ')'
        return node

    def _apply_quantifier(self, node: Any) -> Any:
        """quantifier  ::=  '?' | '*' | '+' | '{' n '}' | '{' n ',' m '}'"""
        if self.pos >= len(self.pattern):
            return node
        c = self.pattern[self.pos]
        if c == '?':
            self.pos += 1
            return Repeat(node, 0, 1)
        if c == '*':
            self.pos += 1
            return Repeat(node, 0, self.max_repeat)
        if c == '+':
            self.pos += 1
            return Repeat(node, 1, self.max_repeat)
        if c == '{':
            return self._parse_brace(node)
        return node

    def _parse_brace(self, node: Any) -> Any:
        """{n} or {n,m}"""
        self.pos += 1          # consume '{'
        start = self.pos
        while self.pos < len(self.pattern) and self.pattern[self.pos] != '}':
            self.pos += 1
        content = self.pattern[start:self.pos]
        self.pos += 1          # consume '}'
        if ',' in content:
            lo_str, hi_str = content.split(',', 1)
            lo = int(lo_str)
            hi = int(hi_str) if hi_str else self.max_repeat
        else:
            lo = hi = int(content)
        return Repeat(node, lo, hi)


# ---------------------------------------------------------------------------
# Generator: AST  →  random valid string  +  processing trace
# ---------------------------------------------------------------------------

class RegexGenerator:
    """
    Walks the AST and produces:
      • a randomly generated string that satisfies the pattern
      • a step-by-step trace of every decision made
    """

    def __init__(self):
        self.steps: List[str] = []
        self._depth: int = 0

    # ── public entry point ──────────────────────────────────────────────────

    def generate(self, ast: Any) -> str:
        self.steps = []
        self._depth = 0
        result = self._gen(ast)
        return result

    # ── internal recursion ──────────────────────────────────────────────────

    def _indent(self) -> str:
        return "  " * self._depth

    def _log(self, msg: str) -> None:
        self.steps.append(f"{self._indent()}{msg}")

    def _gen(self, node: Any) -> str:
        self._depth += 1
        result = ""

        if isinstance(node, Literal):
            if node.char:
                self._log(f"Emit '{node.char}'")
            result = node.char

        elif isinstance(node, Concat):
            self._log(f"Concatenate {len(node.children)} part(s):")
            for child in node.children:
                result += self._gen(child)

        elif isinstance(node, Alternation):
            idx = random.randrange(len(node.options))
            self._log(
                f"Choose alternative {idx + 1} of {len(node.options)}"
            )
            result = self._gen(node.options[idx])

        elif isinstance(node, Repeat):
            count = random.randint(node.min_rep, node.max_rep)
            self._log(
                f"Repeat {count}× (allowed range: {node.min_rep}–{node.max_rep}):"
            )
            for i in range(count):
                if count > 1:
                    self._log(f"  Iteration {i + 1}/{count}:")
                    self._depth += 1
                result += self._gen(node.child)
                if count > 1:
                    self._depth -= 1

        self._depth -= 1
        return result


# ---------------------------------------------------------------------------
# Pretty-print the AST
# ---------------------------------------------------------------------------

def print_ast(node: Any, indent: int = 0) -> None:
    pad = "  " * indent
    if isinstance(node, Literal):
        print(f"{pad}Literal('{node.char}')")
    elif isinstance(node, Concat):
        print(f"{pad}Concat:")
        for child in node.children:
            print_ast(child, indent + 1)
    elif isinstance(node, Alternation):
        print(f"{pad}Alternation:")
        for opt in node.options:
            print_ast(opt, indent + 1)
    elif isinstance(node, Repeat):
        lo, hi = node.min_rep, node.max_rep
        label = f"{lo}..{hi}" if lo != hi else str(lo)
        print(f"{pad}Repeat({label}):")
        print_ast(node.child, indent + 1)
    else:
        print(f"{pad}{node!r}")


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

VARIANT_2_PATTERNS = [
    "M?N{2}(O|P){3}Q*R*",
    "(X|Y|Z){3}8*(9|0)*",
    "(H|I)(J|K)L*N?",
]


def run(patterns: List[str],
        examples_per_pattern: int = EXAMPLES_PER_PATTERN,
        max_repeat: int = MAX_REPEAT) -> None:

    print("=" * 65)
    print("  Lab 4 — Regular Expressions  |  Variant 2")
    print(f"  Max repetitions for * / + : {max_repeat}")
    print("=" * 65)

    for pat_idx, pattern in enumerate(patterns, start=1):
        print(f"\n{'─' * 65}")
        print(f"Pattern {pat_idx}: {pattern}")
        print(f"{'─' * 65}")

        # Parse once, reuse AST for all examples
        parser = RegexParser(pattern, max_repeat)
        ast = parser.parse()

        print("\nAbstract Syntax Tree:")
        print_ast(ast, indent=1)

        generator = RegexGenerator()

        for ex in range(1, examples_per_pattern + 1):
            generated = generator.generate(ast)
            print(f"\n  [Example {ex}]  →  '{generated}'")
            print("  Processing trace:")
            for step in generator.steps:
                print(f"    {step}")

    print(f"\n{'=' * 65}\n")


if __name__ == "__main__":
    run(VARIANT_2_PATTERNS)
