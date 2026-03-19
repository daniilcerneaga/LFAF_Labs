from grammar import Grammar


class FiniteAutomaton:
    """
    Finite Automaton defined by (Q, Sigma, delta, q0, F).

    delta format: {(state, symbol): [next_state, ...]}
    A list with >1 element for a given (state, symbol) means the FA is non-deterministic.

    Variant 5 (Lab 2):
      Q  = {q0, q1, q2, q3}
      Σ  = {a, b}
      F  = {q3}
      q0 = q0
      δ(q0, a) = q1
      δ(q0, b) = q0
      δ(q1, a) = q2   ← same (q1, a) maps to TWO states → NDFA
      δ(q1, a) = q3   ←
      δ(q2, a) = q3
      δ(q2, b) = q0
    """

    def __init__(self, Q, Sigma, delta, q0, F):
        self.Q     = set(Q)
        self.Sigma = set(Sigma)
        self.delta = delta   # {(state, symbol): [next_state, ...]}
        self.q0    = q0
        self.F     = set(F)

    # ------------------------------------------------------------------ #
    #  Lab 1 method (kept for completeness)                               #
    # ------------------------------------------------------------------ #

    def string_belongs_to_language(self, input_string: str) -> bool:
        """Simulate the (N)FA and return True if the string is accepted."""
        current = {self.q0}
        for sym in input_string:
            if sym not in self.Sigma:
                return False
            nxt = set()
            for st in current:
                nxt.update(self.delta.get((st, sym), []))
            current = nxt
            if not current:
                return False
        return bool(current & self.F)

    # ------------------------------------------------------------------ #
    #  Lab 2 — Task a: FA → Regular Grammar                               #
    # ------------------------------------------------------------------ #

    def to_regular_grammar(self) -> Grammar:
        """
        Convert this FA to an equivalent right-linear regular grammar.

        Conversion rules:
          δ(qi, a) = qj  →  qi → a qj
          δ(qi, a) = qj  and qj ∈ F  →  add  qi → a  as well
        """
        V_n = set(str(s) for s in self.Q)
        V_t = set(self.Sigma)
        P   = {str(s): [] for s in self.Q}

        for (state, sym), targets in self.delta.items():
            for tgt in targets:
                # qi → a qj
                P[str(state)].append(sym + str(tgt))
                # if target is final, also add terminal production qi → a
                if tgt in self.F:
                    P[str(state)].append(sym)

        # Remove non-terminals with no productions (dead states)
        P = {k: v for k, v in P.items() if v}

        return Grammar(V_n, V_t, P, str(self.q0))

    # ------------------------------------------------------------------ #
    #  Lab 2 — Task b: Determinism check                                  #
    # ------------------------------------------------------------------ #

    def is_deterministic(self) -> bool:
        """
        Return True iff the FA is deterministic (every (state,symbol)
        pair has at most one target state).
        """
        for (state, sym), targets in self.delta.items():
            if len(targets) > 1:
                return False
        return True

    def get_nondeterministic_transitions(self) -> list:
        """Return list of (state, symbol) pairs that cause non-determinism."""
        nd = []
        for (state, sym), targets in self.delta.items():
            if len(targets) > 1:
                nd.append((state, sym, targets))
        return nd

    # ------------------------------------------------------------------ #
    #  Lab 2 — Task c: Subset construction  NDFA → DFA                   #
    # ------------------------------------------------------------------ #

    def to_dfa(self) -> "FiniteAutomaton":
        """
        Convert this NDFA to an equivalent DFA using the subset construction
        (powerset construction) algorithm.

        Each DFA state is a frozenset of NDFA states.
        """
        start = frozenset({self.q0})
        dfa_states  = set()
        dfa_delta   = {}
        dfa_final   = set()
        queue       = [start]
        visited     = set()

        while queue:
            current_set = queue.pop(0)
            if current_set in visited:
                continue
            visited.add(current_set)
            dfa_states.add(current_set)

            # Mark as final if any NDFA state inside is final
            if current_set & self.F:
                dfa_final.add(current_set)

            for sym in sorted(self.Sigma):
                # Compute union of all reachable states under sym
                next_set = frozenset(
                    ns
                    for st in current_set
                    for ns in self.delta.get((st, sym), [])
                )
                if not next_set:
                    continue   # dead / no transition — omit (partial DFA)

                dfa_delta[(current_set, sym)] = [next_set]

                if next_set not in visited:
                    queue.append(next_set)

        return FiniteAutomaton(dfa_states, self.Sigma, dfa_delta, start, dfa_final)

    # ------------------------------------------------------------------ #
    #  Lab 2 — Bonus: Graphviz DOT representation                         #
    # ------------------------------------------------------------------ #

    def to_dot(self, name: str = "FA") -> str:
        """Return a Graphviz DOT string for visual rendering."""
        def label(s):
            if isinstance(s, frozenset):
                return "{" + ",".join(sorted(str(x) for x in s)) + "}"
            return str(s)

        lines = [f'digraph {name} {{', '  rankdir=LR;',
                 '  node [shape=circle];']

        # Mark final states with double circle
        for f in self.F:
            lines.append(f'  "{label(f)}" [shape=doublecircle];')

        # Invisible start arrow
        lines.append(f'  __start [shape=none, label=""];')
        lines.append(f'  __start -> "{label(self.q0)}";')

        # Group transitions by (src, dst) to merge labels
        edge_labels: dict = {}
        for (src, sym), targets in self.delta.items():
            for tgt in targets:
                key = (label(src), label(tgt))
                edge_labels.setdefault(key, []).append(sym)

        for (src, tgt), syms in edge_labels.items():
            lbl = ",".join(sorted(syms))
            lines.append(f'  "{src}" -> "{tgt}" [label="{lbl}"];')

        lines.append("}")
        return "\n".join(lines)

    def print_transition_table(self):
        """Print a formatted transition table."""
        symbols = sorted(self.Sigma)

        def label(s):
            if isinstance(s, frozenset):
                return "{" + ",".join(sorted(str(x) for x in s)) + "}"
            return str(s)

        states = sorted(self.Q, key=lambda s: label(s))

        # Header
        col = 18
        header = f"{'State':<{col}}" + "".join(f"{sym:<{col}}" for sym in symbols) + "Final?"
        print(header)
        print("-" * len(header))

        for st in states:
            marker = "(start) " if st == self.q0 else "        "
            row = f"{marker + label(st):<{col}}"
            for sym in symbols:
                targets = self.delta.get((st, sym), [])
                cell = ",".join(label(t) for t in targets) if targets else "—"
                row += f"{cell:<{col}}"
            row += "Yes" if st in self.F else "No"
            print(row)

    def __repr__(self):
        def label(s):
            if isinstance(s, frozenset):
                return "{" + ",".join(sorted(str(x) for x in s)) + "}"
            return str(s)
        return (
            f"FiniteAutomaton(\n"
            f"  Q     = {{{', '.join(label(s) for s in sorted(self.Q, key=label))}}},\n"
            f"  Sigma = {sorted(self.Sigma)},\n"
            f"  q0    = {label(self.q0)},\n"
            f"  F     = {{{', '.join(label(s) for s in self.F)}}}\n"
            f")"
        )
