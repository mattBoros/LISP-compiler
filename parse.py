class AST:
    def __init__(self, tokens):
        self.tokens = tokens


def get_func_ast(source):
    source = source.strip().replace('\n', '').replace('  ', ' ')
    if source.startswith('(') or source.startswith('['):
        source = source[1:-1]
    else:
        return source
    tokens = []
    paren_count = 0
    current_token = ''
    for c in source:
        current_token = current_token + c
        if c in ['(', '[']:
            paren_count += 1
        if c in [')', ']']:
            paren_count -= 1
        if paren_count == 0 and c == ' ' and not current_token.isspace():
            tokens.append(current_token.strip())
            current_token = ''
    tokens.append(current_token.strip())
    tokens = [get_func_ast(t) for t in tokens]
    return AST(tokens)
