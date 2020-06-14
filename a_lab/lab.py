class EvaluationError(Exception):
    pass

# splits a program into its tokens 
def tokenize(program):
    # split program into lines to deal with comments 
    program_lines = program.split('\n')
    # removing comments
    for cur_index, line in enumerate(program_lines):
        if ';' in line:
            program_lines[cur_index] = line[:line.index(';')]
    single_program = ' '.join(program_lines)
    return single_program.replace('(', ' ( ').replace(')', ' ) ').split()

def is_valid_parse(tokens):
    open_p = 0
    for token in tokens:
        if token == '(':
            open_p += 1
        elif token == ')':
            open_p -= 1
        if open_p < 0:
            return False
    return open_p == 0

def parsing(tokens):
    initial_token = tokens.pop(0)
    if not tokens:
        try:
            if '.' in initial_token:
                cur_num = float(initial_token)
            else:
                cur_num = int(initial_token)
            return cur_num
        except:
            return initial_token

    cur_list = []
    while tokens[0] != ')':
        if tokens[0] == '(':
            cur_list.append(parsing(tokens))
        else:
            cur_token = tokens.pop(0)
            try:
                if '.' in cur_token:
                    cur_num = float(cur_token)
                else:
                    cur_num = int(cur_token)
                cur_list.append(cur_num)
            except:
                cur_list.append(cur_token)
    tokens.pop(0)
    return cur_list

def parse(tokens):
    if not is_valid_parse(tokens):
        raise SyntaxError
    return parsing(tokens)

'''
~~~~~~~~~~~~~~~~~~~~~~~~~ BUILT-IN FUNCTION DEFINITIONS ~~~~~~~~~~~~~~~~~~~~~~~~~
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
~~~~~~~~~~~~~~~~~~~~~~~~~ HELPER CLASSES ~~~~~~~~~~~~~~~~~~~~~~~~~
'''

class Environment():
    def __init__(self, parent = carlae_builtins):
        self.parent = parent
        self.symbols = {}

    def __setitem__(self, key, val):
        self.symbols[key] = val
    
    def __getitem__(self, key):
        # if key in current environment
        if key in self.symbols:
            return self.symbols[key]
        # if key in carlae_builtins
        elif key in carlae_builtins:
            return carlae_builtins[key]
        # if not in parents
        elif parent == carlae_builtins:
            raise EvaluationError
        # check parents 
        return self.parent[key]

    def set(self, key, value):
        if key not in self.symbols:
            a = 5

def is_valid_eval(parsed):
    a = 6

def result_and_env(parsed, env = None):
    if not env:
        env = Environment()

    # empty list means no program run
    if parsed == []:
        raise EvaluationError

    # single value in expression [1 1.0]
    if isinstance(parsed, list) and (isinstance(parsed[0], int) or isinstance(parsed[0], float)):
        raise EvaluationError 

    # binding that doesn't exist
    if isinstance(parsed, str) and parsed not in env.symbols:
        raise EvaluationError

    # single value not in expression
    if isinstance(parsed, int) or isinstance(parsed, float):
        return parsed, env

    # binding 
    if isinstance(parsed, str):
        return env[parsed], env


    # executing operations
    operation = parsed[0]

    if operation == 'define':
        env[parsed[1]] = result_and_env(parsed[2], env)[0]
        return env[parsed[1]], env

    operands = []
    # evaluate subsequent expressions to perform function on
    for expression in parsed[1:]:
        operands.append(evaluate(expression, env))
    if operation in carlae_builtins:
        return carlae_builtins[operation](operands), env
    else:
        print('undefined operation')


def evaluate(parsed, env = None):
    return result_and_env(parsed, env)[0]


'''
# for repl/testing 
if __name__ == '__main__':
    env = Environment()
    file_name = 'test.txt'
    file = open(file_name, 'r')
    file_program = file.read()
    # print('test output: ', evaluate(parse(tokenize(file_program))), env)

    while True:
        try:
            program = input('in:\n')
            if program == 'quit':
                break
            else:
                # value = evaluate(parse(tokenize(program)), env)
                value = parse(tokenize(program))
                print('out:\n', value, '\n')
        except:
            print('out:\ninvalid program\n')

'''


# program = open('test.txt').read()
# print'original program: ', program
# print evaluate(parse(tokenize(program)))





