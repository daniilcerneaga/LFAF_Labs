from grammar import Grammar
from finite_automaton import FiniteAutomaton


def separator(title: str):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def main():
    # ------------------------------------------------------------------ #
    #  Re-use Lab 1 Grammar (Variant 5)                                   #
    # ------------------------------------------------------------------ #
    separator("Lab 1 Grammar — Variant 5")
    V_n = {"S", "F", "L"}
    V_t = {"a", "b", "c", "d"}
    P = {
        "S": ["bS", "aF", "d"],
        "F": ["cF", "dF", "aL", "b"],
        "L": ["aL", "c"],
    }
    grammar = Grammar(V_n, V_t, P, "S")
    print(grammar)

    # ------------------------------------------------------------------ #
    #  Task 2a — Chomsky classification                                   #
    # ------------------------------------------------------------------ #
    separator("Task 2a — Chomsky Classification")
    chomsky_type = grammar.classify_chomsky()
    print(f"  Grammar type: {chomsky_type}")
    print("  Explanation: All productions are of the form A → aB or A → a")
    print("  (right-linear), which satisfies Type 3 regular grammar rules.")

    # ------------------------------------------------------------------ #
    #  Lab 2 NDFA — Variant 5                                             #
    #  Q = {q0,q1,q2,q3},  Σ = {a,b},  F = {q3}                         #
    #  δ(q0,a)=q1, δ(q0,b)=q0                                            #
    #  δ(q1,a)=q2, δ(q1,a)=q3   ← non-deterministic!                     #
    #  δ(q2,a)=q3, δ(q2,b)=q0                                            #
    # ------------------------------------------------------------------ #
    separator("Lab 2 NDFA — Variant 5")
    ndfa_delta = {
        ("q0", "a"): ["q1"],
        ("q0", "b"): ["q0"],
        ("q1", "a"): ["q2", "q3"],   # NDFA: two targets for same (state, symbol)
        ("q2", "a"): ["q3"],
        ("q2", "b"): ["q0"],
    }
    ndfa = FiniteAutomaton(
        Q={"q0", "q1", "q2", "q3"},
        Sigma={"a", "b"},
        delta=ndfa_delta,
        q0="q0",
        F={"q3"},
    )
    print(ndfa)
    print("\nTransition table:")
    ndfa.print_transition_table()

    # ------------------------------------------------------------------ #
    #  Task 3a — FA to Regular Grammar                                    #
    # ------------------------------------------------------------------ #
    separator("Task 3a — FA → Regular Grammar")
    fa_grammar = ndfa.to_regular_grammar()
    print(fa_grammar)
    chomsky = fa_grammar.classify_chomsky()
    print(f"\n  Chomsky classification: {chomsky}")

    # ------------------------------------------------------------------ #
    #  Task 3b — Determinism check                                        #
    # ------------------------------------------------------------------ #
    separator("Task 3b — Determinism Check")
    det = ndfa.is_deterministic()
    print(f"  Is deterministic: {det}")
    nd_transitions = ndfa.get_nondeterministic_transitions()
    if nd_transitions:
        for state, sym, targets in nd_transitions:
            print(f"  Non-deterministic transition: δ({state}, {sym}) = {targets}")
        print("  → The FA is an NDFA because at least one (state, symbol) pair")
        print("    leads to more than one state.")

    # ------------------------------------------------------------------ #
    #  Task 3c — NDFA → DFA (subset construction)                        #
    # ------------------------------------------------------------------ #
    separator("Task 3c — Subset Construction: NDFA → DFA")
    dfa = ndfa.to_dfa()
    print(dfa)
    print("\nDFA transition table:")
    dfa.print_transition_table()
    print(f"\n  DFA is deterministic: {dfa.is_deterministic()}")

    # ------------------------------------------------------------------ #
    #  Validation on both NDFA and DFA                                    #
    # ------------------------------------------------------------------ #
    separator("String Validation (NDFA vs DFA)")
    test_strings = [
        ("aa",    True),   # q0→q1→q3  ✓
        ("aaa",   True),   # q0→q1→q2→q3  ✓
        ("baaa",  True),   # q0→q0→q1→q2→q3  ✓
        ("baa",   True),   # q0→q0→q1→q3  ✓
        ("aabaa", True),   # q0→q1→q2→q0→q1→q3 ✓
        ("b",     False),
        ("a",     False),
        ("ab",    False),
        ("ba",    False),
        ("bb",    False),
    ]

    print(f"  {'String':<12} {'Expected':<10} {'NDFA':<8} {'DFA':<8} {'Match?'}")
    print("  " + "-" * 52)
    all_ok = True
    for s, expected in test_strings:
        ndfa_res = ndfa.string_belongs_to_language(s)
        dfa_res  = dfa.string_belongs_to_language(s)
        match    = ndfa_res == dfa_res == expected
        if not match:
            all_ok = False
        mark = "✓" if match else "✗"
        print(f"  {s!r:<12} {str(expected):<10} {str(ndfa_res):<8} {str(dfa_res):<8} {mark}")
    print(f"\n  All results consistent: {all_ok}")

    # ------------------------------------------------------------------ #
    #  Bonus — DOT output                                                 #
    # ------------------------------------------------------------------ #
    separator("Bonus — Graphviz DOT Strings")
    print("\n--- NDFA ---")
    print(ndfa.to_dot("NDFA_Variant5"))
    print("\n--- DFA ---")
    print(dfa.to_dot("DFA_Variant5"))


if __name__ == "__main__":
    main()
