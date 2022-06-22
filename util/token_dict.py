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


def id_to_token(i: int) -> str:
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
    return keys[i - 1]
