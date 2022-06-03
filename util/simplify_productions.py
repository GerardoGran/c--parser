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
            values.append(prod.split(" "))  # Split into array separated by " "
        grammar[key] = values   # Insert into grammar

    return grammar, non_terminals


def show_grammar(grammar: dict) -> None:
    """
    Prints the function in "v1->p1 | ... | pn" format.
    Can be output into a .txt file to save as new grammar.

    args
        grammar: previously built grammar dictionary
    """
    str = ""
    for key in grammar:
        prods = []
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
    removed = True
    while removed:
        removed = False
        for key in grammar:
            for i, prod in enumerate(grammar[key]):
                if len(prod) == 1 and prod[0] in non_terminals:
                    for replace in grammar[prod[0]][::-1]:
                        grammar[key].insert(i+1, replace)
                    grammar[key].pop(i)
                    removed = True
    return grammar


grammar, non_terminals = get_grammar_from_txt("producciones.txt")
non_up_grammar = remove_unit_productions(grammar, non_terminals)

show_grammar(non_up_grammar)
