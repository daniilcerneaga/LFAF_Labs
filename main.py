from grammar import Grammar, FiniteAutomaton


def main():
    # ------------------------------------------------------------------ #
    #  Variant 5 grammar definition                                        #
    #  VN = {S, F, L},  VT = {a, b, c, d}                                #
    #  P:                                                                  #
    #    S -> bS | aF | d                                                  #
    #    F -> cF | dF | aL | b                                             #
    #    L -> aL | c                                                       #
    # ------------------------------------------------------------------ #
    V_n = {"S", "F", "L"}
    V_t = {"a", "b", "c", "d"}
    P = {
        "S": ["bS", "aF", "d"],
        "F": ["cF", "dF", "aL", "b"],
        "L": ["aL", "c"],
    }
    S = "S"

    grammar = Grammar(V_n, V_t, P, S)
    print("=== Grammar (Variant 5) ===")
    print(grammar)

    # ------------------------------------------------------------------ #
    #  Task b: Generate 5 valid strings                                    #
    # ------------------------------------------------------------------ #
    print("\n=== 5 Generated Strings ===")
    generated = []
    for i in range(5):
        s = grammar.generate_string()
        generated.append(s)
        print(f"  {i + 1}. '{s}'")

    # ------------------------------------------------------------------ #
    #  Task c: Convert Grammar -> Finite Automaton                         #
    # ------------------------------------------------------------------ #
    fa = grammar.to_finite_automaton()
    print("\n=== Converted Finite Automaton ===")
    print(fa)

    # ------------------------------------------------------------------ #
    #  Task d: Check membership of strings                                 #
    # ------------------------------------------------------------------ #
    print("\n=== Membership Checks ===")

    # All generated strings must be accepted
    print("  Generated strings (should all be ACCEPTED):")
    for s in generated:
        result = fa.string_belongs_to_language(s)
        mark = "✓" if result else "✗"
        print(f"    {mark}  '{s}' -> {result}")

    # Some hand-crafted valid strings
    valid_examples = ["d", "ab", "bbd", "acb", "aac", "bbab", "aadab"]
    print("\n  Hand-crafted valid strings (should be ACCEPTED):")
    for s in valid_examples:
        result = fa.string_belongs_to_language(s)
        mark = "✓" if result else "✗"
        print(f"    {mark}  '{s}' -> {result}")

    # Some invalid strings
    invalid_examples = ["", "a", "ba", "abc", "aa", "bc", "ca"]
    print("\n  Invalid strings (should be REJECTED):")
    for s in invalid_examples:
        result = fa.string_belongs_to_language(s)
        mark = "✓" if not result else "✗"
        print(f"    {mark}  '{s}' -> {result}")


if __name__ == "__main__":
    main()
