from util.create_transition_table import create_transition_table
from util.token_dict import create_token_dict

# list of dictionaries to represent transition table
# usage: transition_table[current_state][current_char]

transition_table = create_transition_table()

# states that reach acceptor states with delims, nums or letters
delim_ended_states = [10, 11, 13, 15, 17, 22]

# token dictionary to translate into symbol table and output
token_dict = create_token_dict()

# keyword list to check if an identifier is a keyword
keywords = ['if', 'else', 'void', 'return', 'int', 'while', 'input', 'output']

# identifier type groups
whitespace = [" ", "\t", "\n", ""]
accepted_chars = ['!', '<', '>', '=', '+', '-', '*',
                  '/', ',', ';', '(', ')', '[', ']', '{', '}']

# error messages
error_messages = ['Invalid Char', 'Identifiers cannot have numbers',
                  'Numbers cannot have letters', "expected '='"]

# scanner output
scanner_output = []

# lines of symbols
lines = []

# empty number and identifier tables
number_symbol_table = []
identifier_symbol_table = []


def identify_char(char: str) -> str:
    """Identifies char to use in transition table.

    Checks if a given char is a letter, digit, or other.

    Args:
        char: The character to identify

    Returns:
        A string identifying if the char is a letter, digit, or itself if otherwise.
    """

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


# when called as a module, run whole program
if __name__ == "__main__":
    # file name, change here
    code_file_name = "test/test2.txt"
    code = open(code_file_name)

    # initialize current identifier and state
    identifier = ""
    state = 0

    prev_char = ""

    line = 1

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

            # append line for token for parser use
            lines.append(line)

            # check if identifier is word
            if state == 10:
                # identifier is a keyword and is added to symbol table directly
                if identifier in keywords:
                    scanner_output.append(token_dict[identifier])
                else:
                    # identifier is not a keyword and is new
                    if identifier not in identifier_symbol_table:
                        # add identifier
                        identifier_symbol_table.append(identifier)

                    # append token 2 and entry no.
                    scanner_output.append(
                        (2, identifier_symbol_table.index(identifier) + 1))

            # check if identifier is number
            elif state == 11:
                num = int(identifier)

                # number is new
                if num not in number_symbol_table:
                    # add number
                    number_symbol_table.append(num)

                # append token 1 and entry no.
                scanner_output.append(
                    (1, number_symbol_table.index(num) + 1))

            else:
                scanner_output.append(token_dict[identifier])

            state = 0
            identifier = ""

        # reset after comment
        if state == 31:
            state = 0
            identifier = ""

        if state >= 32:
            # raise exception from error_messages list
            error_msg = f"{error_messages[state - 32]}: '{identifier}'"

            raise Exception(f"{error_msg} in line {line}")

    print(f"out = {scanner_output}")
    print(f"number_symbol_table = {number_symbol_table}")
    print(f"identifier_symbol_table = {identifier_symbol_table}")
