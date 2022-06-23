import sys
import util.grammar as gram
from scanner import run_scanner
from util.token_dict import id_to_token


def show_symbol_table(symbol_table: list):
    for entry in symbol_table:
        print('\t'.join(entry))
    return


def LL1(grammar: dict, parse_table: dict, input: list, symbol_table: list):
    """
    Runs LL(1) Parsing Algorithm.

    args
        grammar: dict representing grammar derived from .txt
        parse_table: dict of dicts representing LL(1) parsing table
        input: list of lists from scanner output. Must not be empty.

    returns
        bool indicating success.
    """
    # Validate input
    if len(input) == 1 and input[0][1] == 30:
        raise Exception("INPUT: code file cannot be empty")

    non_terminals = list(grammar.keys())
    productions = gram.enumerate_productions(grammar)

    stack = ['$', non_terminals[0]]  # stack with symbols to match
    input_pointer = 0   # pointer to traverse input

    current_nt = ''

    while stack[-1] != '$':
        top = stack[-1]  # assign top to variable for legibility
        # current token from input
        token = id_to_token(input[input_pointer][1])

        print(f'stack: {stack}\ttoken: {token}')

        if top == token:    # if match
            print(f'matched {token}. nt: {current_nt}')

            if token == 'ID' and current_nt == 'declaration':  # matched global fun or var
                next_token = id_to_token(input[input_pointer + 1][1])
                if next_token == '(':
                    symbol_table[input[input_pointer][2] - 1] = [symbol_table[input[input_pointer]
                                                                              [2] - 1]] + ['function', id_to_token(input[input_pointer - 1][1])]
                else:
                    symbol_table[input[input_pointer][2] - 1] = [symbol_table[input[input_pointer]
                                                                              [2] - 1]] + ['var', 'global']

            if token == 'ID' and current_nt == "var_declaration":   # matched local var
                symbol_table[input[input_pointer][2] - 1] = [
                    symbol_table[input[input_pointer][2] - 1]] + ['var', 'local']

            stack.pop()  # remove from stack
            input_pointer += 1  # traverse input

        elif top not in non_terminals:  # if TopStack is terminal without match
            raise Exception(
                f"STACK: Expected {top} got {token} in line {input[input_pointer][0]}")
        # if TopStack is nt and cannot have token
        elif parse_table[top][token] == "ERROR":
            raise Exception(
                f"TABLE: Expected {top} got {token} in line {input[input_pointer][0]}")
        else:   # traverse Parse Table to new production
            production_number = parse_table[top][token]  # production to go to
            # symbols in RHS of production
            production_symbols = productions[production_number]
            print(f'{production_symbols[0]} -> {production_symbols[1:]}')

            current_nt = production_symbols[0]

            stack.pop()   # pop before inserting new symbols
            if "ε" not in production_symbols:   # do not push epsilon
                # insert symbols in reverse
                stack.extend(production_symbols[:0:-1])

    if stack[-1] == '$' and token == '$':  # program ended correctly
        print('-----------SUCCESS-----------')
        show_symbol_table(symbol_table)
        return
    elif input_pointer >= len(input):   # input incomplete
        print(f'stack: {stack}\ttoken: {token}')
        raise Exception(
            f'INPUT: Input ended prematurely, top of stack: {stack[-1]}')
    else:
        print(f'stack: {stack}\ttoken: {token}')    # did not end correctly
        raise Exception(f'TOP: Did not end on $, got {token}')


if __name__ == "__main__":
    # sys.tracebacklimit = 0

    code_file = "test/using.txt"

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

    LL1(grammar, parse_table, scanner_output, identifier_symbol_table)
