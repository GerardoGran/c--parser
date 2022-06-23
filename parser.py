import sys
import util.grammar as gram
from scanner import run_scanner
from util.token_dict import id_to_token


def last_fun_main(symbol_table: list) -> bool:
    """
    Traverses symbol table in reverse until a function is found. If the function is void and called main, accept. 
    """
    for entry in symbol_table[::-1]:
        if entry[1] == 'function':  # last of type function
            # last function is void main()
            if entry[0] == 'main' and entry[2] == 'void':
                return True
            else:
                return False


def show_symbol_table(symbol_table: list):
    """
    Show symbol table in a readable format

    args
        symbol_table: list of identifiers in format {identifier: [type(fun/var), return type or var scope]}
    """
    for entry in symbol_table:
        print('\t'.join(entry))
    return


def initialize_symbol_table(symbol_table: list) -> list:
    """
    Initialize symbol table to be in parser format. [identifier, type(fun/var), return type or var scope]

    args
        symbol_table: list of identifiers from scanner output.

    returns
        symbol_table: list of lists in parser format. [identifier, type(fun/var), return type or var scope]
    """

    for i, identifier in enumerate(symbol_table):
        symbol_table[i] = [identifier, None, None]

    return symbol_table


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
    symbol_table = initialize_symbol_table(symbol_table)

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
                identifier = input[input_pointer][2] - 1
                if next_token == '(':
                    fun_type = id_to_token(input[input_pointer - 1][1])
                    if symbol_table[identifier][0] == 'main':
                        # if not equal, neither is None. Overwriting main
                        if symbol_table[identifier][1] != symbol_table[identifier][2]:
                            raise Exception(
                                f'SEMANTIC ERROR in line{input[input_pointer][0]}: Function void can only be declared once')
                        if fun_type != 'void' or id_to_token(input[input_pointer + 2][1]) != 'void' or id_to_token(input[input_pointer + 3][1]) != ')':
                            raise Exception(
                                f'SEMANTIC ERROR in line{input[input_pointer][0]}: Function main must be type void with single parameter void')

                    symbol_table[identifier][1] = 'function'
                    symbol_table[identifier][2] = fun_type

                    print(
                        f'matched function: {symbol_table[identifier]}')

                else:
                    symbol_table[identifier][1] = 'var'
                    symbol_table[identifier][2] = 'global'

            if token == 'ID' and current_nt == "var_declaration":   # matched local var
                identifier = input[input_pointer][2] - 1
                symbol_table[identifier][1] = 'var'
                symbol_table[identifier][2] = 'local'

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
        if last_fun_main(symbol_table):
            return True
        else:
            raise Exception(
                "SEMANTIC: Last function declaration must be void main(void){}")
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
