def create_token_dict():
    token_dict = {}

    keys = ["NUM",
            "ID",
            "if",
            "else",
            "void",
            "return",
            "int",
            "while",
            "input",
            "output",
            "!=",
            "<",
            "<=",
            ">",
            ">=",
            "=",
            "==",
            "+",
            "-",
            "*",
            "/",
            ",",
            ";",
            "(",
            ")",
            "[",
            "]",
            "{",
            "}",
            "Comment"]

    for i, k in enumerate(keys):
        token_dict[k] = i + 1

    return token_dict
