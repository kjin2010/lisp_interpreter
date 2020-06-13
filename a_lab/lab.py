# splits a program into its tokens 
def tokenize(program):
    # split program into lines to deal with comments 
    program_lines = program.split('\n')
    # removing comments
    for cur_index, line in enumerate(program_lines):
        if ';' in line:
            program_lines[cur_index] = line[:line.index(';')]
    single_program = ''.join(program_lines).replace('(', ' ( ').replace(')', ' ) ')
    return single_program.split()

def parse(tokens):
    # make sure expression exists
    if tokens:
        initial_token = tokens.pop(0)
    else:
        return

    # expressions have to start with parentheses
    if initial_token != '(':
        raise SyntaxError('missing opening parentheses; invalid program')
    # parsed representation of tokens
    cur_parse = []
    # continue if more tokens exist and is not end of expression
    while tokens and tokens[0] != ')':
        # append parsed subexpression 
        if tokens[0] == '(':
            cur_parse.append(parse(tokens))
        # append current token
        else: 
            cur_token = tokens.pop(0)
            try:
                if '.' in cur_token:
                    cur_num = float(cur_token)
                else:
                    cur_num = int(cur_token)
                cur_parse.append(cur_num)
            except:
                cur_parse.append(cur_token)

    # if empty list, missing close parentheses
    if not tokens:
        raise SyntaxError('missing closing parentheses; invalid program')
    # remove it and return current parsed expression
    else:
        tokens.pop(0)
        return cur_parse

'''
BUILT-IN FUNCTION DEFINITIONS
'''

def sub(args):
    if len(args) == 1:
        return -1 * args[0]
    else:
        return args[0] - sum(args[1:])

def mult(args):
    temp = 1
    for val in args:
        temp *= val
    return temp

def div(args):
    if len(args) == 1:
        return 1
    else:
        temp = args[0]
        for val in args[1:]:
            temp /= val
        return temp

carlae_builtins = {
    '+': sum,
    '-': sub,
    '*': mult,
    '/': div,
}

''' 
HELPER CLASSES
'''

class Environment():
    def __init__(self, symbols = carlae_builtins):
        self.symbols = symbols


def evaluate(parsed):
    # error
    if parsed == []:
        raise EvaluationError

    # error
    if isinstance(parsed, list) and (isinstance(parsed[0], int) or isinstance(parsed[0], float)):
        raise EvaluationError 

    # single value
    if isinstance(parsed, int) or isinstance(parsed, float):
        return parsed

    operation = parsed[0]
    operands = []
    for expression in parsed[1:]:
        operands.append(evaluate(expression))
    if operation in carlae_builtins.keys():
        return carlae_builtins[operation](operands)
    else:
        print('undefined operation')

if __name__ == '__main__':
    while True:
        try:
            program = input('in:\n')
            if program == 'quit':
                break
            else:
                print('\nout:\n', evaluate(parse(tokenize(program))))
        except:
            print('\nout:\ninvalid program\n')








