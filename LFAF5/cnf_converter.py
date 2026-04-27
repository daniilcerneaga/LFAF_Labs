"""
Chomsky Normal Form (CNF) Converter
Variant 6 Grammar:
    VN = {S, A, B, C, E}
    VT = {a, b}
    P:
        S -> aB | AC
        A -> a | ASC | BC
        B -> b | bS
        C -> eps | BA
        E -> bB
"""

from copy import deepcopy
from itertools import combinations


class Grammar:
    def __init__(self, VN, VT, P, S):
        """
        VN: set of non-terminals
        VT: set of terminals
        P:  dict mapping non-terminal -> list of productions (each production is a list of symbols)
        S:  start symbol
        """
        self.VN = set(VN)
        self.VT = set(VT)
        self.P = {nt: [list(prod) for prod in prods] for nt, prods in P.items()}
        self.S = S

    def copy(self):
        return Grammar(set(self.VN), set(self.VT), deepcopy(self.P), self.S)

    def print_grammar(self):
        print(f"VN = {sorted(self.VN)}")
        print(f"VT = {sorted(self.VT)}")
        print(f"Start: {self.S}")
        print("Productions:")
        for nt in sorted(self.P.keys()):
            for prod in self.P[nt]:
                rhs = ''.join(prod) if prod else 'ε'
                print(f"  {nt} -> {rhs}")
        print()

    # -------------------------------------------------------------------------
    # Step 1: Eliminate ε-productions
    # -------------------------------------------------------------------------
    def eliminate_epsilon(self):
        # Find all nullable non-terminals
        nullable = set()
        changed = True
        while changed:
            changed = False
            for nt, prods in list(self.P.items()):
                if nt in nullable:
                    continue
                for prod in prods:
                    if prod == [] or all(sym in nullable for sym in prod):
                        nullable.add(nt)
                        changed = True

        # For each production, add versions where nullable symbols are removed
        new_P = {}
        for nt, prods in list(self.P.items()):
            new_prods = set()
            for prod in prods:
                if prod == []:
                    continue  # remove ε production itself
                # find positions of nullable symbols
                nullable_positions = [i for i, sym in enumerate(prod) if sym in nullable]
                # generate all subsets of those positions to remove
                for r in range(len(nullable_positions) + 1):
                    for positions_to_remove in combinations(nullable_positions, r):
                        new_prod = [sym for i, sym in enumerate(prod) if i not in positions_to_remove]
                        if new_prod:  # don't add empty
                            new_prods.add(tuple(new_prod))
            new_P[nt] = [list(p) for p in new_prods]

        # If start symbol is nullable, add S -> ε back
        if self.S in nullable:
            new_P[self.S].append([])

        self.P = new_P
        return nullable

    # -------------------------------------------------------------------------
    # Step 2: Eliminate unit productions (renaming)
    # -------------------------------------------------------------------------
    def eliminate_unit_productions(self):
        changed = True
        while changed:
            changed = False
            new_P = {nt: list(prods) for nt, prods in self.P.items()}
            for nt, prods in list(self.P.items()):
                for prod in prods:
                    if len(prod) == 1 and prod[0] in self.VN:
                        # unit production: nt -> X
                        target = prod[0]
                        # add all productions of target to nt
                        for target_prod in self.P.get(target, []):
                            if target_prod not in new_P[nt]:
                                new_P[nt].append(list(target_prod))
                                changed = True
                        # remove the unit production
                        if prod in new_P[nt]:
                            new_P[nt].remove(prod)
                            changed = True
            self.P = new_P

    # -------------------------------------------------------------------------
    # Step 3: Eliminate inaccessible symbols
    # -------------------------------------------------------------------------
    def eliminate_inaccessible(self):
        reachable = {self.S}
        changed = True
        while changed:
            changed = False
            for nt in list(reachable):
                for prod in self.P.get(nt, []):
                    for sym in prod:
                        if sym in self.VN and sym not in reachable:
                            reachable.add(sym)
                            changed = True

        inaccessible = self.VN - reachable
        for sym in inaccessible:
            self.P.pop(sym, None)
        self.VN = reachable
        return inaccessible

    # -------------------------------------------------------------------------
    # Step 4: Eliminate non-productive symbols
    # -------------------------------------------------------------------------
    def eliminate_nonproductive(self):
        # A symbol is productive if it can derive a string of terminals
        productive = set(self.VT)
        changed = True
        while changed:
            changed = False
            for nt, prods in list(self.P.items()):
                if nt in productive:
                    continue
                for prod in prods:
                    if all(sym in productive for sym in prod):
                        productive.add(nt)
                        changed = True

        nonproductive = self.VN - productive
        # Remove non-productive non-terminals and any production containing them
        for sym in nonproductive:
            self.P.pop(sym, None)
        for nt in list(self.P.keys()):
            self.P[nt] = [prod for prod in self.P[nt]
                          if all(sym not in nonproductive for sym in prod)]
        self.VN = self.VN - nonproductive
        return nonproductive

    # -------------------------------------------------------------------------
    # Step 5: Convert to CNF
    # -------------------------------------------------------------------------
    def to_cnf(self):
        """Convert grammar to Chomsky Normal Form.
        Every production must be either:
          - A -> BC  (two non-terminals)
          - A -> a   (single terminal)
        """
        # Replace terminals in long productions with new non-terminals
        terminal_map = {}  # terminal -> new NT
        new_counter = [0]

        def get_terminal_nt(term):
            if term not in terminal_map:
                new_name = f"T_{term}_{new_counter[0]}"
                new_counter[0] += 1
                terminal_map[term] = new_name
                self.VN.add(new_name)
                self.P[new_name] = [[term]]
            return terminal_map[term]

        new_P = {}
        for nt, prods in list(self.P.items()):
            new_prods = []
            for prod in prods:
                if len(prod) == 1:
                    # Already A -> a or A -> B; keep as is (unit to terminal is fine)
                    new_prods.append(prod)
                elif len(prod) == 2:
                    # Replace any terminal with its NT wrapper
                    new_prod = []
                    for sym in prod:
                        if sym in self.VT:
                            new_prod.append(get_terminal_nt(sym))
                        else:
                            new_prod.append(sym)
                    new_prods.append(new_prod)
                else:
                    # Length >= 3: replace terminals first, then binarize
                    replaced = []
                    for sym in prod:
                        if sym in self.VT:
                            replaced.append(get_terminal_nt(sym))
                        else:
                            replaced.append(sym)
                    # Binarize: A -> B1 B2 B3 => A -> B1 X, X -> B2 B3
                    while len(replaced) > 2:
                        new_name = f"X_{new_counter[0]}"
                        new_counter[0] += 1
                        self.VN.add(new_name)
                        new_P[new_name] = [replaced[-2:]]
                        replaced = replaced[:-2] + [new_name]
                    new_prods.append(replaced)
            new_P[nt] = new_prods

        # Add terminal wrapper productions
        for nt, prods in list(self.P.items()):
            if nt not in new_P:
                new_P[nt] = prods

        self.P = new_P


def convert_to_cnf(grammar: Grammar, verbose=True) -> Grammar:
    """Convert a grammar to CNF step by step."""
    g = grammar.copy()

    if verbose:
        print("=" * 60)
        print("ORIGINAL GRAMMAR")
        print("=" * 60)
        g.print_grammar()

    # Step 1
    nullable = g.eliminate_epsilon()
    if verbose:
        print("=" * 60)
        print(f"STEP 1: Eliminate ε-productions")
        print(f"  Nullable symbols: {nullable}")
        print("=" * 60)
        g.print_grammar()

    # Step 2
    g.eliminate_unit_productions()
    if verbose:
        print("=" * 60)
        print("STEP 2: Eliminate unit (renaming) productions")
        print("=" * 60)
        g.print_grammar()

    # Step 3
    inaccessible = g.eliminate_inaccessible()
    if verbose:
        print("=" * 60)
        print(f"STEP 3: Eliminate inaccessible symbols")
        print(f"  Inaccessible: {inaccessible}")
        print("=" * 60)
        g.print_grammar()

    # Step 4
    nonproductive = g.eliminate_nonproductive()
    if verbose:
        print("=" * 60)
        print(f"STEP 4: Eliminate non-productive symbols")
        print(f"  Non-productive: {nonproductive}")
        print("=" * 60)
        g.print_grammar()

    # Step 5
    g.to_cnf()
    if verbose:
        print("=" * 60)
        print("STEP 5: Convert to Chomsky Normal Form")
        print("=" * 60)
        g.print_grammar()

    return g


# ---------------------------------------------------------------------------
# Variant 6 grammar definition
# ---------------------------------------------------------------------------
def get_variant6_grammar() -> Grammar:
    VN = {'S', 'A', 'B', 'C', 'E'}
    VT = {'a', 'b'}
    P = {
        'S': [['a', 'B'], ['A', 'C']],
        'A': [['a'], ['A', 'S', 'C'], ['B', 'C']],
        'B': [['b'], ['b', 'S']],
        'C': [[], ['B', 'A']],          # [] represents ε
        'E': [['b', 'B']],
    }
    return Grammar(VN, VT, P, 'S')


if __name__ == '__main__':
    # --- Variant 6 ---
    print("Running CNF conversion for Variant 6 grammar...")
    g6 = get_variant6_grammar()
    cnf = convert_to_cnf(g6, verbose=True)

    # --- Demo: accept any grammar ---
    print("\n" + "=" * 60)
    print("DEMO: Custom grammar (A -> aAb | ε, S -> AA | b)")
    print("=" * 60)
    custom = Grammar(
        VN={'S', 'A'},
        VT={'a', 'b'},
        P={
            'S': [['A', 'A'], ['b']],
            'A': [['a', 'A', 'b'], []],
        },
        S='S'
    )
    convert_to_cnf(custom, verbose=True)
