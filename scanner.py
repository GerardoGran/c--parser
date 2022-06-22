from util.create_transition_table import create_transition_table
from util.token_dict import create_token_dict


def identify_char(char: str) -> str:
    """Identifies char to use in transition table.

    Checks if a given char is a letter, digit, or other.

    Args:
        char: The character to identify

    Returns:
        A string identifying if the char is a letter, digit, or itself if otherwise.
    """
    # identifier type groups
    whitespace = [" ", "\t", "\n", ""]
    accepted_chars = ['!', '<', '>', '=', '+', '-', '*',
                      '/', ',', ';', '(', ')', '[', ']', '{', '}']

    # return letter for transition table if char is a letter
    if char.isalpha():
        return "letter"

    # return digit for transition table if char is a digit
    elif char.isdigit():
        return "digit"

    elif char in whitespace:
        return "delim"

    # return char itself if it is an accepted character
    elif char in accepted_chars:
        return char
    else:
        return "bad_char"


def run_scanner(code_file: str, verbose: bool = False):
    """
    Runs the scanner.

    args
        code_file: a str with the file location and name of the source code.

    returns
        scanner_output: list of lists with tokenIDs in format [line, ID, (position in symbol table)]
        number_symbol_table: list of numbers
        identifier_symbol_table: list of identifiers
    """
    # file name, change here
    code = open(code_file)

    # initialize current identifier and state
    identifier = ""
    state = 0

    prev_char = ""

    line = 1

    transition_table = create_transition_table()

    # states that reach acceptor states with delims, nums or letters
    delim_ended_states = [10, 11, 13, 15, 17, 22]

    # token dictionary to translate into symbol table and output
    token_dict = create_token_dict()

    # keyword list to check if an identifier is a keyword
    keywords = ['if', 'else', 'void', 'return',
                'int', 'while', 'input', 'output']

    # error messages
    error_messages = ['Invalid Char', 'Identifiers cannot have numbers',
                      'Numbers cannot have letters', "expected '='"]

    # scanner output
    scanner_output = []

    # empty number and identifier tables
    number_symbol_table = []
    identifier_symbol_table = []

    # loop forever, reading 1 char at a time...
    while True:
        # deal with leftover char after acceptor state
        if prev_char == "":
            char = code.read(1).lower()
        # "double up" on leftover char
        else:
            # if delim was newline, substract 1 from line to avoid counting double newline
            if prev_char == "\n":
                line -= 1
            char = prev_char
            prev_char = ""  # ensure this only happens once

        # track line of code
        if char == "\n":
            line += 1

        # ...until we reach null character, meaning EOF
        if not char and identifier == "":
            if verbose:
                print("End of source code file.")
            code.close()
            break

        # translate char into transition
        transition = identify_char(char)

        # change state
        state = transition_table[state][transition]

        # ignore blanks
        if state == 0:
            continue

        identifier += char

        # check if state is acceptor
        if state >= 10 and state <= 30:
            # handle leftover character when ending in a delimiter
            if state in delim_ended_states and char != "":  # confirm char != "" to avoid removing identifier

                # assign last char of identifier to prev_char
                prev_char = identifier[-1]

                # remove last char from identifier
                identifier = identifier[:-1]

            # check if identifier is word
            if state == 10:
                # identifier is a keyword and is added to symbol table directly
                if identifier in keywords:
                    scanner_output.append([line, token_dict[identifier]])
                else:
                    # identifier is not a keyword and is new
                    if identifier not in identifier_symbol_table:
                        # add identifier
                        identifier_symbol_table.append(identifier)

                    # append token 2 and entry no.
                    scanner_output.append(
                        [line, 2, identifier_symbol_table.index(identifier) + 1])

            # check if identifier is number
            elif state == 11:
                num = int(identifier)

                # number is new
                if num not in number_symbol_table:
                    # add number
                    number_symbol_table.append(num)

                # append token 1 and entry no.
                scanner_output.append(
                    [line, 1, number_symbol_table.index(num) + 1])

            else:
                scanner_output.append([line, token_dict[identifier]])

            state = 0
            identifier = ""

        # reset after comment
        if state == 31:
            state = 0
            identifier = ""

        if state >= 32:
            # raise exception from error_messages list
            error_msg = f"{error_messages[state - 32]}: '{identifier}'"

            raise Exception(f"LEXICAL ERROR: {error_msg} in line {line}")

    return scanner_output, number_symbol_table, identifier_symbol_table


# when called as a module, run whole program
if __name__ == "__main__":

    scanner_output, number_symbol_table, identifier_symbol_table = run_scanner(
        "test/test2.txt")

    print(f"out = {scanner_output}")
    print(f"number_symbol_table = {number_symbol_table}")
    print(f"identifier_symbol_table = {identifier_symbol_table}")
