import sys

# custom exception 
class EvaluationError(Exception):
    pass

'''
~~~~~~~~~~~~~~~~~~~~~~~~~ PROGRAM PREPROCESSING ~~~~~~~~~~~~~~~~~~~~~~~~~
'''

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
        # beginning of new subexpression
        if tokens[0] == '(':
            # append parsed subexpression
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

def equals(args):
    for i in args[1:]:
        if i != args[0]:
            return False
    return True

def greater_than(args):
    sort_list = sorted(set(args), reverse = True)
    return args == sort_list

def greater_than_equal(args):
    sort_list = sorted(args, reverse = True)
    return args == sort_list

def less_than(args):
    sort_list = sorted(set(args))
    return args == sort_list

def less_than_equal(args):
    sort_list = sorted(args)
    return args == sort_list

def not_op(args):
    return not args[0]

def list_init(args):
    if args == []:
        return None
    next_list = list_init(args[1:])
    return LinkedList(args[0], next_list)

def car(args):
    if args[0] == None:
        raise EvaluationError
    return args[0].elt

def cdr(args):
    if args[0] == None:
        raise EvaluationError
    return args[0].next

def list_len(args):
    if not args[0]:
        return 0
    return len(args[0])

def elt_at_ind(args):
    my_list = args[0]
    index = args[1]
    if my_list == None:
        raise EvaluationError
    return my_list[index]

def concatenate(args):
    # empty list
    if args == []:
        return None
    # single list
    if len(args) == 1:
        return args[0].copy()
    else:
        # fake empty list for concat compatibility
        head = LinkedList('None', None)
        for concat_list in args:
            # skip empty lists
            if concat_list == None:
                continue
            head.concat(concat_list)
        return head

def map_fun(args):
    func = args[0]
    params = args[1]
    # fake empty list for concat compatibility
    out_list = LinkedList('None', None)
    for x in params:
        out_list.concat(list_init([func([x])]))
    return out_list

def filter_fun(args):
    func = args[0]
    params = args[1]
    # fake empty list for concat compatibility
    out_list = LinkedList('None', None)
    for x in params:
        if func([x]):
            out_list.concat(list_init([x]))
    return out_list

def reduce_fun(args):
    func = args[0]
    params = args[1]
    out_val = args[2]
    for x in params:
        out_val = func([out_val, x])
    return out_val

# base operator dictionary
carlae_builtins = {
    '+': sum,
    '-': sub,
    '*': mult,
    '/': div,
    '=?': equals,
    '>': greater_than,
    '>=': greater_than_equal,
    '<': less_than,
    '<=': less_than_equal,
    'not': not_op,
    '#t': True,
    '#f': False,
    'list': list_init,
    'car': car,
    'cdr': cdr,
    'length': list_len,
    'elt-at-index': elt_at_ind,
    'concat': concatenate,
    'map': map_fun,
    'filter': filter_fun,
    'reduce': reduce_fun,
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
class Function():  
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

# representation of lists
class LinkedList():
    def __init__(self, elt, next):
        # current value
        self.elt = elt
        # pointer to next list node
        self.next = next

    # concatenation function
    def concat(self, new_list):
        # custom case for concatenating to empty list
        if self.elt == 'None':
            self.elt = new_list.elt
            self.next = new_list.next
        # adding copy to tail
        else:
            my_tail = self.get_tail()
            my_tail.next = new_list.copy()

    # returns tail of list 
    # assumes non-empty list
    def get_tail(self):
        current = self
        if current.next == None:
            return self
        while current.next != None:
            current = current.next
        return current

    # returns duplicate of current list
    # used in concatenation
    def copy(self):
        if self.elt == 'None':
            return LinkedList('None', None)
        cur_elt = self.elt
        next_list = None if self.next == None else self.next.copy()
        return LinkedList(cur_elt, next_list)

    # ensures iterability
    def __iter__(self):
        current = self
        while current != None:
            yield current.elt
            current = current.next

    # simplifies recursive symbol fetching
    def __getitem__(self, index):
        current = self
        if len(self) == 0 or index >= len(self) or index < 0:
            raise EvaluationError
        for i in range(index):
            current = current.next
        return current.elt

    # length of list
    def __len__(self):
        counter = 0
        current = self
        while current != None:
            counter += 1
            current = current.next
        return counter

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

    # nested function calls
    if isinstance(first_term, list):
        env['temp_func'] = result_and_env(first_term, env)[0]
        first_term = 'temp_func'

    # function definition
    if first_term == 'lambda':
        return Function(parsed[1], parsed[2], env), env

    # if statement
    if first_term == 'if':
        valid = result_and_env(parsed[1], env)[0]
        exp = parsed[2] if valid else parsed[3]
        return result_and_env(exp, env)[0], env

    # and statement 
    # not in carlae_builtin for short circuiting
    if first_term == 'and':
        for expression in parsed[1:]:
            valid = result_and_env(expression, env)[0]
            # short circuit check
            if not valid:
                return False, env
        return True, env

    # or statement
    # not in carlae_builtin for short circuiting
    if first_term == 'or':
        for expression in parsed[1:]:
            valid = result_and_env(expression, env)[0]
            # short circuit check
            if valid:
                return True, env
        return False, env

    # begin expression
    if first_term == 'begin':
        for expression in parsed[1:]:
            last_val = evaluate(expression, env)
        return last_val, env

    # let expression
    if first_term == 'let':
        # list of vars and values
        bounded = parsed[1]
        # body to be evaluated and returned
        body = parsed[2]
        # creating subenvironment
        sub_env = Environment(env)
        for var in bounded:
            # updating values in subenvironment
            sub_env[var[0]] = result_and_env(var[1], sub_env)[0]
        return result_and_env(body, sub_env)[0], env

    # set! expression
    if first_term == 'set!':
        var_name = parsed[1]
        new_val = result_and_env(parsed[2], env)[0]
        cur_env = env
        # checking all parent envs until no more or in current env
        while cur_env != carlae_builtins and var_name not in cur_env.symbols:
            cur_env = cur_env.parent
        # raise error if not in cur_env
        if cur_env == carlae_builtins:
            raise EvaluationError
        # set value in cur_env
        else:
            cur_env[var_name] = new_val
            return new_val, env


    # simple operator in carlae_builtins
    operands = []
    operation = env[first_term]
    for expression in parsed[1:]:
        operands.append(result_and_env(expression, env)[0])
    # performing operation on operands
    return operation(operands), env

# wrapper function
def evaluate(parsed, env = None):
    return result_and_env(parsed, env)[0]

# reading from file
def evaluate_file(file_name, env = None):
    my_file = open(file_name, 'r')
    program = my_file.read()
    my_file.close()
    return result_and_env(parse(tokenize(program)), env)[0]

''' 
~~~~~~~~~~~~~~~~~~~~~~~~~ REPL AND FILE LOADING ~~~~~~~~~~~~~~~~~~~~~~~~~
'''     

# for REPL/testing 
if __name__ == '__main__':
    # defining global environment
    env = Environment()

    for file_name in sys.argv[1:]:
        evaluate_file(file_name, env)

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
