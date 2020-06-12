from enum import Enum
import re

# splits a program into its tokens 
def tokenize(program):
    search_words = '(\s|=|\(|\)|;)'
    dirty_split = re.split(search_words, program)
    repetitions = ['', ' ']
    # removing spaces and blank tokens
    for token in repetitions:
        while token in dirty_split:
            dirty_split.remove(token)
    # function to clear tokens from every ; to \n
    remove_comments(dirty_split)
    while '\n' in dirty_split:
        dirty_split.remove('\n')
    return dirty_split

# helper function that removes comment tokens
def remove_comments(tokens):
    is_comment = False
    i = 0
    while i < len(tokens):
        # if comment
        if is_comment:
            # end of comment
            if tokens[i] == '\n':
                is_comment = False
            # delete regardless if end of comment or not 
            del(tokens[i])
        # if start of comment
        elif tokens[i] == ';':
            is_comment = True
            del(tokens[i])
        # if not comment or start of comment, increment index
        else:
            i += 1

def parse(tokens):
    a = 5

my_file = open('test.txt', 'r')
program = my_file.read()
my_tokens = tokenize(program)
print(my_tokens)

a = [1, 2, 3, 4]

