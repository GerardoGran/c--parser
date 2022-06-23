import sys
import util.grammar as gram
from scanner import run_scanner
from util.token_dict import id_to_token


def LL1(grammar: dict, parse_table: dict, input: list):
    # Validate input
    if len(input) == 1 and input[0][1] == 30:
        raise Exception("INPUT: code file cannot be empty")

    # input.append('$')

    non_terminals = list(grammar.keys())
    productions = gram.enumerate_productions(grammar)

    stack = ['$', non_terminals[0]]
    input_pointer = 0

    while stack[-1] != '$':
        top = stack[-1]
        if input_pointer < len(input):
            token = id_to_token(input[input_pointer][1])
        print(f'stack: {stack}\ttoken: {token}')
        if top == token:
            print(f'matched {token}')
            stack.pop()
            input_pointer += 1

        elif top not in non_terminals:
            raise Exception(
                f"STACK: Expected {top} got {token} in line {input[input_pointer][0]}")
        elif parse_table[top][token] == "ERROR":
            raise Exception(
                f"TABLE: Expected {top} got {token} in line {input[input_pointer][0]}")
        else:
            production_number = parse_table[top][token]  # production to go to
            # symbols in RHS of production
            production_symbols = productions[production_number]

            stack.pop()   # pop before inserting new symbols
            if production_symbols != ["ε"]:   # do not push epsilon
                # insert symbols in reverse
                stack.extend(production_symbols[::-1])

    if stack[-1] == '$' and token == '$':  # program ended correctly
        print('-----------SUCCESS-----------')
        return
    elif input_pointer >= len(input):
        print(f'stack: {stack}\ttoken: {token}')
        raise Exception(
            f'INPUT: Input ended prematurely, top of stack: {stack[-1]}')
    else:
        print(f'stack: {stack}\ttoken: {token}')
        raise Exception(f'TOP: Did not end on $, got {token}')


if __name__ == "__main__":
    sys.tracebacklimit = 0

    code_file = "test/test9.txt"

    # Run scanner
    scanner_output, number_symbol_table, identifier_symbol_table = run_scanner(
        code_file, verbose=True)

    # Create Parser sets and table
    grammar, non_terminals, terminals = gram.get_grammar_from_txt(
        "util/grammar.txt")
    first_sets = gram.get_first_sets(grammar, non_terminals)
    follow_sets = gram.get_follow_sets(grammar, non_terminals, first_sets)
    first_plus_sets = gram.get_first_plus_sets(
        grammar, non_terminals, first_sets, follow_sets)

    parse_table = gram.create_parse_table(
        grammar, terminals, first_plus_sets)

    LL1(grammar, parse_table, scanner_output)
