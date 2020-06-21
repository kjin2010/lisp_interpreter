# custom exception 
class EvaluationError(Exception):
    pass

# splits a program into its tokens 
def tokenize(program):
    # split program into lines to handle comments 
    program_lines = program.split('\n')
    # removing comments
    for cur_index, line in enumerate(program_lines):
        if ';' in line:
            program_lines[cur_index] = line[:line.index(';')]
    # recombining lines into single string
    single_program = ' '.join(program_lines)
    # spacing parentheses to help with parsing
    return single_program.replace('(', ' ( ').replace(')', ' ) ').split()

# determines if function is valid
def is_valid_parse(tokens):
    # counter for open parentheses - close parentheses
    open_p = 0
    for token in tokens:
        if token == '(':
            open_p += 1
        elif token == ')':
            open_p -= 1
        # if ever more close parentheses, invalid
        if open_p < 0:
            return False
    return open_p == 0

# splits tokens into sub environments
# assumes valid program
def parsing(tokens):
    initial_token = tokens.pop(0)
    # if token is single value
    if not tokens:
        # if numerical value
        try:
            # decimal value
            if '.' in initial_token:
                cur_num = float(initial_token)
            # int value
            else:
                cur_num = int(initial_token)
            return cur_num
        except:
            return initial_token
    # current environment 
    cur_list = []
    # continue parsing until end of current environment
    while tokens[0] != ')':
        # beginning of new subenvironment
        if tokens[0] == '(':
            # append parsed subenvironment
            cur_list.append(parsing(tokens))
        # continuously add components of current environment to parsed list
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
    # remove close parentheses
    tokens.pop(0)
    # return parsed list of current environment
    return cur_list

# parse container function
def parse(tokens):
    # raise error if invalid program
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

# base operator dictionary
carlae_builtins = {
    '+': sum,
    '-': sub,
    '*': mult,
    '/': div,
}

''' 
~~~~~~~~~~~~~~~~~~~~~~~~~ HELPER CLASSES ~~~~~~~~~~~~~~~~~~~~~~~~~
'''

# representation of environments 
class Environment():
    def __init__(self, parent = carlae_builtins):
        # parent environments for recursive symbol retrieval
        self.parent = parent
        # symbols defined in current env
        self.symbols = {}

    # defining symbol in current env
    def __setitem__(self, key, val):
        self.symbols[key] = val
    
    # retrieving value of symbol
    def __getitem__(self, key):
        # check current env's symbol table
        if key in self.symbols:
            return self.symbols[key]
        # check parent env if is not carlae_builtins
        elif self.parent != carlae_builtins:
            return self.parent[key]
        # check carlae_builtins
        else:
            if key in carlae_builtins:
                return carlae_builtins[key]
            else:
                raise EvaluationError

# representation of function information
class Lambda():
    def __init__(self, params, function, env):
        # list of parameters for function
        self.params = params
        # code for execution of function
        self.function = function
        # env where function was defined
        self.env = env

    # calling functions
    def __call__(self, params):
        # if number of params is not correct
        if len(self.params) != len(params):
            raise EvaluationError
        # temporary environment for parameter name mapping
        cur_env = Environment(self.env)
        # mapping parameters to function passed arguments
        for i, var in enumerate(self.params):
            cur_env[var] = params[i]
        # calling function in sub environment
        return result_and_env(self.function, cur_env)[0]

''' 
~~~~~~~~~~~~~~~~~~~~~~~~~ EVALUATION FUNCTIONS ~~~~~~~~~~~~~~~~~~~~~~~~~
'''     

# evaluates expression
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

# wrapper function
def evaluate(parsed, env = None):
    return result_and_env(parsed, env)[0]

# for REPL/testing 
if __name__ == '__main__':
    # defining global environment
    env = Environment()

    # REPL environment
    while True:
        try:
            program = input('in:\n')
            if program == 'quit':
                break
            else:
                value = evaluate(parse(tokenize(program)), env)
                print('out:\n', value, '\n')
        except:
            print('out:\ninvalid program\n')
