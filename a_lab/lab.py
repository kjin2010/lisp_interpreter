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
        # check current symbol table
        if key in self.symbols:
            return self.symbols[key]

        # check parent env if not carlae_builtins
        elif self.parent != carlae_builtins:
            return self.parent[key]

        # check carlae_builtins
        else:
            if key in carlae_builtins:
                return carlae_builtins[key]
            else:
                raise EvaluationError

    def __str__(self):
        return str(self.symbols)

class Lambda():
    def __init__(self, params, function, env):
        self.params = params
        self.function = function
        self.env = env

    def __call__(self, params):
        cur_env = Environment(self.env)
        if len(self.params) != len(params):
            raise EvaluationError
        for i, var in enumerate(self.params):
            cur_env[var] = params[i]
        return result_and_env(self.function, cur_env)[0]


def result_and_env(parsed, env = None):
    if not env:
        env = Environment()

    # empty expression
    if parsed == []:
        raise EvaluationError
    # expression begins with value: [1 2]
    if isinstance(parsed, list) and (isinstance(parsed[0], int) or isinstance(parsed[0], float)):
        raise EvaluationError
    # single value not in expression: 1
    if isinstance(parsed, int) or isinstance(parsed, float):
        return parsed, env
    # single value that is binded: val
    if isinstance(parsed, str):
        return env[parsed], env

    # operation execution
    first_term = parsed[0]

    # variable definition
    if first_term == 'define':
        # easier function definition
        if isinstance(parsed[1], list):
            parsed[2] = ['lambda', parsed[1][1:], parsed[2]]
            parsed[1] = parsed[1][0]
            return result_and_env(parsed, env)
        symbol = parsed[1]
        val = result_and_env(parsed[2], env)[0]
        env[symbol] = val
        return val, env

    # function definition
    if first_term == 'lambda':
        return Lambda(parsed[1], parsed[2], env), env

    # nested function calls
    if isinstance(first_term, list):
        env['temp_func'] = result_and_env(first_term, env)[0]
        first_term = 'temp_func'

    # simple operator in carlae_builtins
    operands = []
    operation = env[first_term]
    for expression in parsed[1:]:
        operands.append(result_and_env(expression, env)[0])

    return operation(operands), env


def evaluate(parsed, env = None):
    return result_and_env(parsed, env)[0]


# '''
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
                value = evaluate(parse(tokenize(program)), env)
                # value = parse(tokenize(program))
                print('out:\n', value, '\n')
        except:
            print('out:\ninvalid program\n')

# '''


# program = open('test.txt').read()
# print'original program: ', program
# print parse(tokenize(program))





