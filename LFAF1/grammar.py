import random


class FiniteAutomaton:
    """
    Finite Automaton defined by:
      Q     - set of states
      Sigma - input alphabet
      delta - transition function: dict {(state, symbol): [next_states]}
      q0    - initial state
      F     - set of final/accept states
    """

    def __init__(self, Q, Sigma, delta, q0, F):
        self.Q = Q
        self.Sigma = Sigma
        self.delta = delta   # {(state, symbol): [next_state, ...]}
        self.q0 = q0
        self.F = F

    def string_belongs_to_language(self, input_string: str) -> bool:
        """
        Check whether input_string is accepted by this FA.
        Uses BFS/simulation over all possible current states (handles NFA).
        """
        current_states = {self.q0}

        for symbol in input_string:
            if symbol not in self.Sigma:
                return False
            next_states = set()
            for state in current_states:
                for ns in self.delta.get((state, symbol), []):
                    next_states.add(ns)
            current_states = next_states
            if not current_states:
                return False

        return bool(current_states & self.F)

    def __repr__(self):
        return (
            f"FiniteAutomaton(\n"
            f"  Q={self.Q},\n"
            f"  Sigma={self.Sigma},\n"
            f"  delta={self.delta},\n"
            f"  q0={self.q0!r},\n"
            f"  F={self.F}\n"
            f")"
        )


class Grammar:
    """
    Regular Grammar defined by:
      V_n - non-terminals
      V_t - terminals
      P   - production rules (dict: non-terminal -> list of right-hand sides)
      S   - start symbol

    Variant 5:
      VN = {S, F, L}
      VT = {a, b, c, d}
      P:
        S -> bS | aF | d
        F -> cF | dF | aL | b
        L -> aL | c
    """

    def __init__(self, V_n, V_t, P, S):
        self.V_n = V_n
        self.V_t = V_t
        self.P = P      # {non_terminal: ["rhs1", "rhs2", ...]}
        self.S = S

    def generate_string(self) -> str:
        """
        Randomly derive a string from the grammar starting from S.
        Each RHS is either:
          - a terminal alone            (e.g. "d", "b", "c")
          - a terminal + non-terminal   (e.g. "bS", "aF", "aL")
        """
        result = ""
        current = self.S

        while current in self.V_n:
            productions = self.P[current]
            chosen = random.choice(productions)

            if len(chosen) == 1:
                # Pure terminal
                result += chosen
                current = None          # derivation ends
            else:
                # Terminal followed by non-terminal
                result += chosen[0]
                current = chosen[1]

        return result

    def to_finite_automaton(self) -> FiniteAutomaton:
        """
        Convert this right-linear grammar to an equivalent NFA.

        Conversion rules:
          A -> aB   becomes  delta(A, a) contains B
          A -> a    becomes  delta(A, a) contains FINAL
        A new accepting state FINAL is added to F.
        """
        FINAL = "FINAL"
        Q = set(self.V_n) | {FINAL}
        Sigma = set(self.V_t)
        delta = {}
        F = {FINAL}
        q0 = self.S

        for non_term, productions in self.P.items():
            for rhs in productions:
                if len(rhs) == 1:
                    # A -> a  =>  delta(A, a) -> FINAL
                    terminal = rhs[0]
                    key = (non_term, terminal)
                    delta.setdefault(key, []).append(FINAL)
                else:
                    # A -> aB  =>  delta(A, a) -> B
                    terminal = rhs[0]
                    next_state = rhs[1]
                    key = (non_term, terminal)
                    delta.setdefault(key, []).append(next_state)

        return FiniteAutomaton(Q, Sigma, delta, q0, F)

    def __repr__(self):
        return (
            f"Grammar(\n"
            f"  V_n={self.V_n},\n"
            f"  V_t={self.V_t},\n"
            f"  P={self.P},\n"
            f"  S={self.S!r}\n"
            f")"
        )
