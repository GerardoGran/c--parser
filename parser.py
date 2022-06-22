import grammar


def LL1(grammar: dict, parse_table: dict, input: ):
    non_terminals = list(grammar.keys())
    stack = ['$', non_terminals[0]]

    top = stack.pop()
    return
