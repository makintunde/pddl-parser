import re


def scan_tokens(filename):
    # TODO: Replace 'tokens' with AST?
    with open(filename, 'r') as f:
        # Remove single line comments
        str = re.sub(r';.*$', '', f.read(), flags=re.MULTILINE).lower()
    # Tokenize
    stack = []
    list = []
    for t in re.findall(r'[()]|[^\s()]+', str):
        if t == '(':
            stack.append(list)
            list = []
        elif t == ')':
            if stack:
                l = list
                list = stack.pop()
                list.append(l)
            else:
                raise Exception('Missing open parentheses')
        else:
            list.append(t)
    if stack:
        raise Exception('Missing close parentheses')
    if len(list) != 1:
        raise Exception('Malformed expression')
    return list[0]
