import random


class Grammar:
    """
    Regular Grammar defined by (V_N, V_T, P, S).

    Variant 5 (Lab 1):
      VN = {S, F, L},  VT = {a, b, c, d}
      P:
        S -> bS | aF | d
        F -> cF | dF | aL | b
        L -> aL | c
    """

    def __init__(self, V_n, V_t, P, S):
        self.V_n = set(V_n)
        self.V_t = set(V_t)
        self.P = P      # {non_terminal: ["rhs1", "rhs2", ...]}
        self.S = S

    # ------------------------------------------------------------------ #
    #  Lab 1 methods                                                       #
    # ------------------------------------------------------------------ #

    def generate_string(self) -> str:
        """Randomly derive a string from the grammar starting from S."""
        result = ""
        current = self.S

        while current in self.V_n:
            productions = self.P[current]
            chosen = random.choice(productions)

            if len(chosen) == 1:
                result += chosen
                current = None
            else:
                result += chosen[0]
                current = chosen[1]

        return result

    def to_finite_automaton(self):
        """Convert this right-linear grammar to an equivalent NFA."""
        from finite_automaton import FiniteAutomaton

        FINAL = "FINAL"
        Q = self.V_n | {FINAL}
        Sigma = set(self.V_t)
        delta = {}
        F = {FINAL}
        q0 = self.S

        for non_term, productions in self.P.items():
            for rhs in productions:
                if len(rhs) == 1:
                    key = (non_term, rhs[0])
                    delta.setdefault(key, []).append(FINAL)
                else:
                    key = (non_term, rhs[0])
                    delta.setdefault(key, []).append(rhs[1])

        return FiniteAutomaton(Q, Sigma, delta, q0, F)

    # ------------------------------------------------------------------ #
    #  Lab 2 — Chomsky hierarchy classifier                                #
    # ------------------------------------------------------------------ #

    def classify_chomsky(self) -> str:
        """
        Classify this grammar according to the Chomsky hierarchy.

        Type 3 (Regular):
          All productions are of the form A → aB  or  A → a
          (right-linear) or A → Ba  or  A → a  (left-linear),
          where A,B ∈ V_N and a ∈ V_T.

        Type 2 (Context-Free):
          All productions have a single non-terminal on the LHS.

        Type 1 (Context-Sensitive):
          For every production α → β:  |α| ≤ |β|
          (except possibly S → ε if S never appears on a RHS).

        Type 0 (Unrestricted):
          Everything else.

        Returns a string describing the type.
        """
        is_right_linear = True
        is_left_linear  = True
        is_context_free = True
        is_context_sens = True

        for lhs, productions in self.P.items():
            # Context-Free check: LHS must be a single non-terminal
            if lhs not in self.V_n:
                is_context_free = False
                is_right_linear = False
                is_left_linear  = False

            for rhs in productions:
                # Context-Sensitive: |lhs| <= |rhs|  (allow ε only from start)
                if len(rhs) < len(lhs):
                    if not (rhs == "" and lhs == self.S):
                        is_context_sens = False

                # Check right-linear: A → a  or  A → aB
                if not self._is_right_linear(rhs):
                    is_right_linear = False

                # Check left-linear: A → a  or  A → Ba
                if not self._is_left_linear(rhs):
                    is_left_linear = False

        if is_right_linear or is_left_linear:
            return "Type 3 - Regular Grammar"
        if is_context_free:
            return "Type 2 - Context-Free Grammar"
        if is_context_sens:
            return "Type 1 - Context-Sensitive Grammar"
        return "Type 0 - Unrestricted Grammar"

    def _is_right_linear(self, rhs: str) -> bool:
        """
        Check if rhs matches A → a  or  A → aB.
        Supports multi-character non-terminal names (e.g. 'q0', 'q1').
        """
        if len(rhs) == 0:
            return True   # ε-production allowed
        # Try every split: first part must be a single terminal,
        # remainder (if any) must be a non-terminal.
        for i in range(1, len(rhs) + 1):
            terminal_part    = rhs[:i]
            nonterminal_part = rhs[i:]
            if terminal_part in self.V_t:
                if nonterminal_part == "" or nonterminal_part in self.V_n:
                    return True
        return False

    def _is_left_linear(self, rhs: str) -> bool:
        """
        Check if rhs matches A → a  or  A → Ba.
        Supports multi-character non-terminal names.
        """
        if len(rhs) == 0:
            return True
        # Try every split: last part must be a single terminal,
        # prefix (if any) must be a non-terminal.
        for i in range(len(rhs)):
            nonterminal_part = rhs[:i]
            terminal_part    = rhs[i:]
            if terminal_part in self.V_t:
                if nonterminal_part == "" or nonterminal_part in self.V_n:
                    return True
        return False

    def __repr__(self):
        lines = ["Grammar(", f"  V_n={sorted(self.V_n)},",
                 f"  V_t={sorted(self.V_t)},", "  P={"]
        for nt, prods in sorted(self.P.items()):
            lines.append(f"    {nt!r}: {prods},")
        lines.append(f"  }},\n  S={self.S!r}\n)")
        return "\n".join(lines)
