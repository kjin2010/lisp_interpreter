from enum import Enum
import re

class Token(Enum):
    LEFT_P = '('
    RIGHT_P = ')'

left_p = '('
if (left_p == Token.LEFT_P.value):
    print('true')

a = '( there are = sometimes  \n b = 5 )'
b = re.split('(\s+|\=|\(|\))', a)
print(b) 

c = 'a  b c d e'
d = re.split('\s+', c)
print(d)