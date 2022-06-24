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
        entry = map(lambda x: 'None' if x is None else x, entry)
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


def get_global_variables(symbol_table: list) -> set:
    """
    Gets set of global variables in format {('name', scope_lvl)}
    """
    globals = set()
    for entry in symbol_table:
        if entry[2] == 'global':
            globals.add((entry[0], -1))
    return globals


def remove_level_of_scope(vars: set, scope_lvl: int) -> set:
    """
    Removes all vars lower that the specified level of scope, making them inaccessible
    """
    scoped_vars = set()
    for var in vars:
        if var[1] < scope_lvl:
            scoped_vars.add(var)

    return scoped_vars


def in_scope(var_name: str, scoped_vars: set) -> bool:
    for var in scoped_vars:
        if var_name == var[0]:
            return True
    return False


def handle_error_stack(token: str, line: int, productions: dict, n: int):
    print(
        f'\n\nTOKEN: {token}\tProduction {n}: {productions[n][0]} -> {productions[n][1:]}')

    error_msgs = [
        f"Program must begin with a function or variable declaration.",
        f"Program must begin with a function or variable declaration.",
        f"Invalid declaration. Variables can only be int. Functions can only be Void.",
        f"Invalid declaration. Variables can only be int. Functions can only be Void.",
        f"Invalid declaration. 'int' must be followed by a valid identifier.",
        f"Invalid void function declaration. Must be of format 'void ID(params) {{}}'.",
        f"Invalid variable declaration. Must be of format 'int ID;'.",
        f"Invalid array declaration. Must be of format 'int ID[NUM];'.",
        f"Invalid int function declaration. Must be of format 'int ID(params) {{}}'.",
        f"Invalid variable declaration. 'int' must be followed by a valid identifier.",
        f"Invalid variable declaration. Must be of format 'int ID;'.",
        f"Invalid array declaration. Must be of format 'int ID[NUM];'.",
        f"Invalid parameters. If multiple parameters, they must be of type int.",
        f"Invalid parameters. Only one parameter allowed for 'void' parameters.",
        f"Invalid parameters. Parameters must be separated by commas ','.",
        f"Invalid parameters. Parameter list must be closed by a parenthesis ')'.",
        f"Invalid parameter. int params must be valid identifiers.",
        f"Invalid parameter. Array parameters must not have a size in format 'int ID[]'.",
        f"Invalid parameters. List of parameters must close on a ')' and be separated by commas ','.",
        f"Invalid function body. The body of a function must be enclosed by brackets '{{}}'.",
        f"Invalid local declaration. Variables can only be ints.",
        f"Invalid statement. Cannot do operations outside of an assignment, comparison, function call, or array call.",
        f"Invalid statement. Cannot do operations outside of an assignment, comparison, function call, or array call.",
        f"Invalid statement. No declarations may be after the first statement in a scope. Statements must begin with an ID or keyword.",
        f"Invalid statement. Cannot call or assign to an invalid ID.",
        f"Invalid statement. Must be encompased by brackets '{{}}'.",
        f"Invalid if statement. Must be of format 'if (expression) statement' with an optional 'else statement'.",
        f"Invalid while statement. Must be of format 'while (expression) statement'.",
        f"Invalid return statement.",
        f"Invalid input statement. Must be followed by an existing variable in format 'input var;'.",
        f"Invalid output statement. Must be followed by an existing variable in format 'output var;'.",
        f"Invalid assignment statement. Can only assign to a valid var or array element in format 'ID = expression;'",
        f"Invalid function call. Must be called with args between parentheses in format 'ID(args)'.",
        f"Invalid else statement. Must begin with 'else' keyword and be followed by another statement.",
        f"Invalid else statement. Must begin with 'else' keyword and be followed by another statement.",
        f"Invalid void return statement.",
        f"Invalid int return statement. Must return an expression or variable.",
        f"Invalid input statement. Must be followed by an existing variable in format 'input var;'.",
        f"Invalid input statement. Must be followed by an existing variable in format 'input var[position];'.",
        f"Invalid var declaration or assignment.",
        f"Invalid expression.",
        f"Invalid relational expression.",
        f"Invalid expression. Must begin with an ID or keyword.",
        f"Invalid relational operator. The only relational operators are '<, >, <=, >=, ==, !='.",
        f"Invalid relational operator. The only relational operators are '<, >, <=, >=, ==, !='.",
        f"Invalid relational operator. The only relational operators are '<, >, <=, >=, ==, !='.",
        f"Invalid relational operator. The only relational operators are '<, >, <=, >=, ==, !='.",
        f"Invalid relational operator. The only relational operators are '<, >, <=, >=, ==, !='.",
        f"Invalid relational operator. The only relational operators are '<, >, <=, >=, ==, !='.",
        f"Invalid arithmetic expression. Expressions can only be done with NUMs IDs.",
        f"Invalid arithmetic expression. May only have one operator. Operators may only be '-, +, *, /'.",
        f"Invalid arithmetic expression. May only have one operator. Operators may only be '-, +, *, /'.",
        f"Incomplete arithmetic expression. Missing second term.",
        f"Incomplete arithmetic expression. Missing second term.",
        f"Invalid arithmetic expression. Expressions can only be done with NUMs IDs.",
        f"Invalid arithmetic expression. May only have one operator. Operators may only be '-, +, *, /'.",
        f"Invalid arithmetic expression. May only have one operator. Operators may only be '-, +, *, /'.",
        f"Incomplete arithmetic expression. Missing second term.",
        f"Incomplete arithmetic expression. Missing second term.",
        f"Invalid arithmetic expression. May only have one operator. Operators may only be '-, +, *, /'.",
        f"Invalid arithmetic expression. Expressions can only be done with NUMs IDs.",
        f"Invalid arithmetic expression. Expressions can only be done with NUMs IDs.",
        f"Invalid array call. Array elements must be called with a NUM or an expression that resolves to an int.",
        f"Invalid arithmetic expression. May only have one operator. Operators may only be '-, +, *, /'.",
        f"Invalid function call. Function call must be 'fun_name(params)'.",
        f"Invalid function call. Arguments must resolve to an int with a NUM, ID or expression.",
        f"Invalid function call. Unclosed arguments list. Must end in ')'.",
        f"Invalid function call. Arguments must resolve to an int with a NUM, ID or expression.",
        f"Invalid function call. Arguments must be separated by commas ','.",
        f"Invalid function call. Unclosed arguments list. Must end in ')'."]

    raise Exception(
        f'SYNTAX ERROR in line {line}: {error_msgs[n - 1]} Got {token}')


def handle_error_table(top: str, token: str, line: int):

    if top == "program":
        error = f"Program must begin with a declaration."
    elif top == "declaration_list":
        error = f"Declaration must begin with int or void."
    elif top == "declaration":
        error = f"Declaration must begin with int or void."
    elif top == "declaration'":
        error = f"A function declaration must include '(params)'. Variable name must be followed by ';' or '[SIZE]'."
    elif top == "var_declaration":
        error = f"Variables can only be int."
    elif top == "var_declaration'":
        error = f"Variable name must be followed by ';' or '[SIZE]'."
    elif top == "params":
        error = f"Parameter definition must be list of ints or a single void."
    elif top == "param_list":
        error = f"List of parameters must be separated by commas ',' and closed by a parenthesis ')'."
    elif top == "param":
        error = f"Params can only be of type int once another int has been declared as a param."
    elif top == "param'":
        error = f"List of parameters must be separated by commas ',' and closed by a parenthesis ')'."
    elif top == "compound_stmt":
        error = f"The body of a statement must begin with brackets '{{'."
    elif token in ['!=', '==', '<', '<=', '>', '>=']:
        error = f"Relational operators may only exist in a relational expression."
    elif token == 'NUM':
        error = f"Numbers may only be used in relational and arithmetic expressions, to access arrays or as params."
    elif token in ['+', '/', '+', '-']:
        error = f"Arithmetic operators may only exist in an arithmetic expression."
    elif token == '=':
        error = f"Assignments can only be done after declarations and to variables."
    elif token == ';':
        error = f"Unexpected ';'. May only be used after a complete statement."
    elif token in '[]':
        error = f"Square brackets may only be used after an ID to access an array's element."
    elif token in '{}':
        error = f"Brackets may only be used to open or close statement bodies."
    elif token == 'void':
        error = f"'void' may only be used to define functions or to indicate null parameters."
    elif token == ',':
        error = f"Commas may only be used to separate parameters or arguments."
    elif token == 'else':
        error = f"Else statements may only be declared after closing an if statement."
    elif token in '()':
        error = f"Parentheses may only be used in function declarations, calls, or logical or arithmetic expressions."
    elif token == "if" or token == "while":
        error = f"If and While statements may only be used inside a function body."
    elif token == 'return':
        error = f"Return statements may only be used inside function declarations."
    elif top == "local_declarations":
        error = f""
    elif top == "statement_list":
        error = f"After the first statement in a function body, no more declarations may be made."
    elif top == "statement":
        error = f"After the first statement in a function body, no more declarations may be made."
    elif top == "statement'":
        error = f"Did not end statement correctly."
    elif top == "selection_stmt":
        error = f"After the first statement in a function body, no more declarations may be made."
    elif top == "return_stmt":
        error = f"No other statements or declarations may be made to return."
    elif top == "var":
        error = f"vars must be a valid ID"
    elif top == "var'":
        error = f"Invalid var."
    elif top == "expression":
        error = f"Expressions must begin with an ID."
    elif top == "expression'":
        error = f"Did not end expression correctly"
    elif top == "relop":
        error = f"Relational operators are '!=, ==, >, >=, <, <=='"
    elif top == "arithmetic_expression":
        error = f"An arithmetic expression must begin with an identifier."
    elif top == "arithmetic_expression'":
        error = f"Did not end arithmetic expression correctly."
    elif top == "addop":
        error = f"Can only add or substract with '+' or '-'."
    elif top == "term":
        error = f"An arithmetic expression must begin with an identifier."
    elif top == "term'":
        error = f"Did not end arithmetic expression correctly."
    elif top == "mulop":
        error = f"Can only multiply or divide with '*' or '/'."
    elif top == "factor":
        error = f"An arithmetic expression must begin with an identifier."
    elif top == "factor'":
        error = f"Did not end arithmetic expression correctly."
    elif top == "call":
        error = f""
    elif top == "args":
        error = f""
    elif top == "args_list":
        error = f""

    raise Exception(
        f'SYNTAX ERROR in line {line}: {error} Got {token}')


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

    production_number = 0

    stack = ['$', non_terminals[0]]  # stack with symbols to match
    input_pointer = 0   # pointer to traverse input
    symbol_table = initialize_symbol_table(symbol_table)

    current_nt = ''

    current_scope = set()  # set of accessible variables in scope
    scope_lvl = 0   # lvl of scope for vars

    while stack[-1] != '$':
        top = stack[-1]  # assign top to variable for legibility
        # current token from input
        token = id_to_token(input[input_pointer][1])

        print(f'stack: {stack}\ttoken: {token}')

        if top == token:    # if match
            print(f'matched {token}. nt: {current_nt}')

            if token == 'ID':   # matched ID
                identifier = input[input_pointer][2] - 1  # identifier position
                identifier_name = symbol_table[identifier][0]
                print(identifier_name)
                if current_nt == 'declaration':  # matched global fun or var

                    next_token = id_to_token(input[input_pointer + 1][1])

                    if next_token == '(':   # matched fun
                        current_scope = get_global_variables(symbol_table)
                        print(f'current_scope: {current_scope}')
                        fun_type = id_to_token(input[input_pointer - 1][1])
                        if identifier_name == 'main':   # matched main function
                            # if not equal, neither is None. Overwriting main
                            if symbol_table[identifier][1] != None:
                                raise Exception(
                                    f'SEMANTIC ERROR in line {input[input_pointer][0]}: Function main can only be declared once')
                            if fun_type != 'void' or id_to_token(input[input_pointer + 2][1]) != 'void' or id_to_token(input[input_pointer + 3][1]) != ')':
                                raise Exception(
                                    f'SEMANTIC ERROR in line {input[input_pointer][0]}: Function main must be type void with single parameter void')

                        symbol_table[identifier][1] = 'function'
                        symbol_table[identifier][2] = fun_type

                    else:   # matched global var
                        if identifier_name == 'main':
                            raise Exception(
                                f'SEMANTIC ERROR in line {input[input_pointer][0]}: Variable cannot be named main')

                        symbol_table[identifier][1] = 'var'
                        symbol_table[identifier][2] = 'global'

                        current_scope = current_scope.union(
                            get_global_variables(symbol_table))
                        print(f'current_scope: {current_scope}')

                if current_nt == 'var_declaration':   # matched local var
                    if identifier_name == 'main':
                        raise Exception(
                            f'SEMANTIC ERROR in line {input[input_pointer][0]}: Variable cannot be named main')
                    symbol_table[identifier][1] = 'var'
                    symbol_table[identifier][2] = 'local'
                    current_scope.add((identifier_name, scope_lvl))
                    print(f'current_scope: {current_scope}')

                if current_nt == 'statement':   # assigning var or calling function
                    next_token = id_to_token(input[input_pointer + 1][1])
                    if next_token == '(':  # calling function
                        # if equal, function has not been declared.
                        if symbol_table[identifier][1] == None:
                            raise Exception(
                                f'SEMANTIC ERROR in line {input[input_pointer][0]}: Function {identifier_name} has not been declared')
                        elif symbol_table[identifier][1] != 'function':
                            raise Exception(
                                f'SEMANTIC ERROR in line {input[input_pointer][0]}: {identifier_name} is not a function and cannot be called')
                        elif identifier_name == 'main':
                            raise Exception(
                                f'SEMANTIC ERROR in line {input[input_pointer][0]}: main function cannot be called')
                    elif next_token == '=':  # assigning variable
                        if symbol_table[identifier][1] == None:
                            raise Exception(
                                f'SEMANTIC ERROR in line {input[input_pointer][0]}: Var {identifier_name} has not been declared')
                        elif symbol_table[identifier][1] == 'function':
                            raise Exception(
                                f'SEMANTIC ERROR in line {input[input_pointer][0]}: Cannot assign value to function {identifier_name}')
                        elif not in_scope(identifier_name, current_scope):
                            raise Exception(
                                f'SEMANTIC ERROR in line {input[input_pointer][0]}: {identifier_name} not in scope of statement')

                if current_nt == 'param':  # parameters in function declaration
                    # only exists in params
                    if symbol_table[identifier][1] == symbol_table[identifier][2]:
                        # both equal to allow overwriting in global or local variables
                        symbol_table[identifier][1] = 'param'
                        symbol_table[identifier][2] = 'param'
                        current_scope.add((identifier_name, scope_lvl))
                        print(f'current_scope: {current_scope}')

                if current_nt == 'factor':  # doing math
                    # if function does not return value
                    if symbol_table[identifier][2] == 'void':
                        raise Exception(
                            f'SEMANTIC ERROR in line {input[input_pointer][0]}: {identifier_name} does not return a value. Cannot be factor')
                    # elif symbol_table[identifier][1] != 'function' and not in_scope(identifier_name, current_scope):
                        # raise Exception(f'SEMANTIC ERROR in line {input[input_pointer][0]}: {identifier_name} not in scope of statement')

                # if current_nt == 'var':  # var is only accessed in input

            elif token == '{':
                scope_lvl += 1
            elif token == '}':
                current_scope = remove_level_of_scope(current_scope, scope_lvl)
                scope_lvl -= 1
            stack.pop()  # remove from stack
            input_pointer += 1  # traverse input

        # if TopStack is terminal without match
        elif top not in non_terminals:
            handle_error_stack(token, input[input_pointer]
                               [0], productions, production_number)
        elif parse_table[top][token] == "ERROR":
            handle_error_table(top, token, input[input_pointer][0])
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

    code_file = "test/test2.txt"

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
