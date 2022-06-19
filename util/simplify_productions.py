def get_grammar_from_txt(txt_name: str) -> tuple:
    """
    Turns a .txt file in the format "v1->p1 | ... | pn" into a dictionary for local processing.

    args
        txt_name: location of the .txt file

    returns
        grammar: dict where key is V and values are P
        non_terminals: a set representing V
    """
    f = open(txt_name, "r")
    productions_str = f.read().split("\n")  # Arr with each V and its productions

    grammar = {}    # Empty dict for storing
    non_terminals = set()   # Set for non_terminals
    grammar_symbols = set()

    for entry in productions_str:
        if entry == "":  # Empty line edge case
            continue
        # Separates into non-terminal and productions
        prod_arr = entry.split("->")
        key = prod_arr[0]
        non_terminals.add(key)
        productions = prod_arr[1].split("|")
        values = []
        for prod in productions:
            prod = prod.strip()  # Remove leading and trailing whitespace
            RH_symbols = prod.split(" ")  # Split into array separated by " "
            values.append(RH_symbols)
            grammar_symbols.update(RH_symbols)
        grammar[key] = values   # Insert into grammar

    terminals = grammar_symbols.difference(non_terminals)
    terminals.add("$")
    return grammar, non_terminals, terminals


def show_grammar(grammar: dict) -> None:
    """
    Prints the function in "v1->p1 | ... | pn" format.
    Can be output into a .txt file to save as new grammar.

    args
        grammar: previously built grammar dictionary
    """
    str = ""
    for key in grammar:
        prods = []  # list to show productions
        for prod in grammar[key]:
            prods.append(" ".join(prod))
        value = " | ".join(prods)
        str += f"{key}->{value}\n"
    print(str)
    return


def remove_unit_productions(grammar: dict, non_terminals: set):
    """
    Removes all unit productions in grammar.

    args
        grammar: previously built grammar dictionary
        non_terminals: set of all non-terminals in grammar

    returns
        grammar: the grammar free of all unit productions
    """
    removed = True  # bool to confirm any change was made
    while removed:
        removed = False  # set to false to avoid infinite loop
        for key in grammar:
            # num of prod and prod to insert in place
            for i, prod in enumerate(grammar[key]):
                # len == 1 and prod in non_temrinal when only 1 symbol is in present and it is part of V
                if len(prod) == 1 and prod[0] in non_terminals:
                    # replaces non-terminal with its productions
                    for replace in grammar[prod[0]][::-1]:
                        grammar[key].insert(i+1, replace)
                    grammar[key].pop(i)  # removes non-terminal
                    removed = True  # set to true to note a change was made
    return grammar


def get_first_sets(grammar: dict, non_terminals: set) -> dict:
    """
    Gets first sets for each non-terminal symbol.
    Goes in reverse order from keys to ensure other symbols have their first() sets complete.

    args
        grammar: previously built grammar dictionary
        non_terminals: set of all non-terminals in grammar

    returns
        first_sets: dictionary of sets with each symbol's first set
    """
    first_sets = dict()  # Dictionary with first sets

    pending = set()  # Set with non-terminals pending to find first sets
    # Iterate through keys in reverse order
    # move in reverse order to reduce pending nt's
    for symbol in list(grammar.keys())[::-1]:
        current_set = set()
        for production in grammar[symbol]:
            first_symbol = production[0]
            if first_symbol in non_terminals:   # if nt, first = first(nt)
                if first_symbol in first_sets.keys():   # ensure first(nt) has been calculated before
                    # first(X) = first(X) ∪ first(Y)
                    current_set = current_set.union(first_sets[first_symbol])
                else:
                    # if first(nt) hasn't been calculated, add to pending
                    pending.add(symbol)
            else:
                current_set.add(first_symbol)   # add terminal symbol

        first_sets[symbol] = current_set    # store current set in dict

    for symbol in pending:  # repeat for all pending nt's
        current_set = set()
        for production in grammar[symbol]:
            first_symbol = production[0]
            if first_symbol in non_terminals:
                if first_symbol in first_sets.keys():
                    current_set = current_set.union(first_sets[first_symbol])
                else:
                    pending.add(symbol)
            else:
                current_set.add(first_symbol)
        first_sets[symbol] = current_set

    return first_sets


def get_follow_sets(grammar: dict, non_terminals: set, first_sets: dict) -> dict:
    """
    Gets follow sets for each non-terminal symbol.

    args
        grammar: previously built grammar dictionary
        non_terminals: set of all non-terminals in grammar
        first_sets: dictionary of sets with each symbol's first set

    returns
        follow: dictionary of sets with each symbol's follow set
    """
    follow = dict()

    # initialize empty follow sets
    for symbol in non_terminals:
        follow[symbol] = set()
    # run through grammar 5 times to ensure all follows are accounted for
    for n in range(5):
        for i, key in enumerate(list(grammar.keys())):
            if i == 0:
                # add $ follow to starting symbol in grammar
                follow[key].add("$")
            for production in grammar[key]:
                for j, symbol in enumerate(production):  # go through each symbol
                    if symbol in non_terminals:
                        if j == len(production) - 1:
                            follow[symbol] = follow[symbol].union(follow[key])
                            break
                        for follow_symbol in production[j+1:]:
                            ended_eps = False
                            if follow_symbol not in non_terminals:
                                follow[symbol].add(follow_symbol)
                                break
                            elif "ε" in first_sets[follow_symbol]:
                                follow[symbol] = follow[symbol].union(
                                    first_sets[follow_symbol])
                                ended_eps = True
                            else:
                                follow[symbol] = follow[symbol].union(
                                    first_sets[follow_symbol])
                                break
                        if ended_eps:
                            follow[symbol] = follow[symbol].union(follow[key])

    # remove epsilons
    for symbol in follow:
        if "ε" in follow[symbol]:
            follow[symbol].remove("ε")

    return follow


def get_first_plus_sets(grammar: dict, non_terminals: set, first_sets: dict, follow_sets: dict) -> dict:
    """
    Gets first+ sets for each non-terminal symbol.

    args
        grammar: previously built grammar dictionary
        non_terminals: set of all non-terminals in grammar
        first_sets: dictionary of sets with each symbol's first set
        follow_sets: dictionary of sets with each symbol's follow set

    returns
        first_plus: dictionary of sets with each symbol's first_plus set
    """
    first_plus = dict()

    for key in list(grammar.keys()):
        for production in grammar[key]:
            production_key = f"{key}->{' '.join(production)}"
            first_plus[production_key] = set()
            for j, symbol in enumerate(production):
                if symbol not in non_terminals:
                    first_plus[production_key].add(
                        symbol)
                    if symbol == "ε":
                        first_plus[production_key] = first_plus[production_key].union(
                            follow_sets[key])
                    break
                else:
                    if "ε" not in first_sets[symbol]:
                        first_plus[production_key] = first_sets[symbol]
                        break
                    else:
                        nt_first = first_sets[symbol]
                        nt_first.remove("ε")
                        first_plus[production_key] = nt_first.union(
                            first_plus[production_key])

                        if j == len(production) - 1:    # if last symbol is nt with ε
                            first_plus[production_key] = first_sets[symbol].union(
                                follow_sets[key])

    return first_plus


def show_sets(type: str, sets: dict, grammar: dict = None):
    if grammar:
        for symbol in grammar:
            print(f"{type}({symbol}) = {{{', '.join(sets[symbol])}}}")
    else:
        for key in sets:
            print(f"{type}({key}) = {{{', '.join(sets[key])}}}")


def create_parse_table(grammar: dict, non_terminals: set, terminals: set, first_plus_sets: dict):
    """
    Creates parse table to get transitions for parser

    args
        grammar: previously built grammar dictionary
        non_terminals: set of all non-terminals in grammar
        terminals: set of all terminals in grammar
        first_plus_sets: dictionary of sets with each production's first plus set

    returns
        parse_table: dictionary of dictionaries representing de parse table
    """
    parse_table = {}

    non_terminals_list = list(grammar.keys())
    terminals_list = list(terminals)
    terminals_list.sort()

    n = 1
    for nt in non_terminals_list:
        parse_table[nt] = {}
        for t in terminals_list:
            parse_table[nt][t] = "ERROR"
        for production in grammar[nt]:
            production_key = f"{nt}->{' '.join(production)}"
            for t in first_plus_sets[production_key]:
                parse_table[nt][t] = n
            n += 1

    print(f"non-terminals,{','.join(terminals_list)}")
    for nt in non_terminals_list:
        s = f"{nt},"
        for t in terminals_list:
            s += f"{parse_table[nt][t]},"
        s = s[:-1]
        print(s)

    return parse_table


grammar, non_terminals, terminals = get_grammar_from_txt("producciones.txt")
first_sets = get_first_sets(grammar, non_terminals)
follow_sets = get_follow_sets(grammar, non_terminals, first_sets)
first_plus_sets = get_first_plus_sets(
    grammar, non_terminals, first_sets, follow_sets)
parse_table = create_parse_table(
    grammar, non_terminals, terminals, first_plus_sets)

# show_grammar(grammar)
# show_sets("FIRST", first_sets, grammar)
# show_sets("FOLLOW", follow_sets, grammar)
# show_sets("FIRST+", first_plus_sets)
