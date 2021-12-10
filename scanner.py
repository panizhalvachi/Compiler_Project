# Mehrshad Mirmohammad 98109634
# Paniz Halvachi 98109729

import string
from typing import List

'''
 we use out DFA class to implement a simple dfa
 it does not support traversing the dfa directly
 what we can ask what is the next state if we are at state x and next char is c.
 also it saves for each transition, that if the transition will consume that char c. 
 it is this way to simply look-ahead. (e.g. when traveling those 'other' transitions). 
'''


class DFA:
    def __init__(self, num_states: int, acc_states: List[int]):
        self.num_states = num_states
        self.trans = [[] for _ in range(num_states)]
        self.accept = [False] * num_states
        for acc in acc_states:
            self.accept[acc] = True

    def add_trans(self, from_node: int, end_node: int, chars: str, is_included=True):
        self.trans[from_node].append((chars, is_included, end_node))

    def next_state(self, cur_node: int, char):
        for (chars, is_included, end_node) in self.trans[cur_node]:
            if char in chars:
                return end_node, is_included
        return None


'''
 here we define the dfa
 note that add_trans will add a transition between 2 nodes with the set of chars for that transition.
 this way a transition can accept multiple char's (like dfa's in the class).
 we use \0 as EOF. also we can have any printable ascii char in out comments (whitespaces included). 
'''

main_dfa = DFA(15, [1, 3, 5, 9, 12, 13])

digit = "0123456789"
sym = "[](){}+-*<;:,="
whitespace = " \n\f\r\v\t"
lower = string.ascii_lowercase
upper = string.ascii_uppercase
valid_chars = upper + lower + whitespace + "[](){}+-<;:,=\0" + digit  # does not include * and / and \0

# Symbols
main_dfa.add_trans(0, 14, "*")
main_dfa.add_trans(14, 1, sym + digit + whitespace + lower + upper, False)
main_dfa.add_trans(0, 1, "[](){}+-<;:,")
main_dfa.add_trans(0, 2, "=")
main_dfa.add_trans(2, 1, "=")
main_dfa.add_trans(2, 3, "/\0" + sym + digit + whitespace + lower + upper, False) # not sure
# Num
main_dfa.add_trans(0, 4, digit)
main_dfa.add_trans(4, 4, digit)
main_dfa.add_trans(4, 5, sym + whitespace + "/\0", False)  # without ID or Keyword
# comment
main_dfa.add_trans(0, 6, "/")
main_dfa.add_trans(6, 7, "*")
main_dfa.add_trans(7, 7, '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&\'()+,-./:;<=>?@['
                         '\\]^_`{|}~ \n\t\r\x0b\x0c')
main_dfa.add_trans(6, 10, "/")
main_dfa.add_trans(10, 10, '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&\'()*+,-./:;<=>?@['
                           '\\]^_`{|}~ \t\r\x0b\x0c')
main_dfa.add_trans(10, 9, "\n\0")  # and EOF
main_dfa.add_trans(7, 8, "*")
main_dfa.add_trans(8, 8, "*")
main_dfa.add_trans(8, 7, "[](){}+-<;:,=" + digit + whitespace + lower + upper)
main_dfa.add_trans(8, 9, "/")
# ID & Keyword
main_dfa.add_trans(0, 11, lower + upper)
main_dfa.add_trans(11, 11, digit + lower + upper)
main_dfa.add_trans(11, 12, "/\0" + sym + whitespace, False)
# whitespaces
main_dfa.add_trans(0, 13, whitespace)

KEYWORDS = ["if", "else", "void", "int", "repeat", "break", "until", "return", "endif"]

linen = 1  # indicates which line we are now
input_path = "input.txt"
input_stream = open(input_path, 'r')

EOF = False


# this func will give us the next char from the input,
# if we reach EOF, first it will return \0 and then it will return none
def get_next_char():
    global EOF
    next_char = input_stream.read(1)
    if next_char == '':
        if not EOF:
            EOF = True
            return '\0'
        else:
            return None
    return next_char


cur_char = get_next_char()  # current char that we should process


# we should call this function to get the next token,
# it will return the class and the token it self,
# if it gets an error, it will raise and Exception with the appropriate error message
# if we reach EOF, it will return none
def get_next_token():
    global linen, cur_char
    cur_node = 0  # start state
    token = ""  # current token

    if cur_char == '\0':  # if we reach the EOF, return none
        cur_char = get_next_char()
        return '$'

    while True:  # read char from input one by one until we find a valid token or an error occurs
        if cur_char is None:  # if we reach EOF, return none
            return '$'

        next_node = main_dfa.next_state(cur_node, cur_char)  # find the next state base on current one and the next char

        # if this char can not be traversed (panic mode) or the transition consume that char :
        if (next_node is None or next_node[1] is True) and not (cur_node == 6 and cur_char in valid_chars):
            # replace cur)char with the next one and add the previous one to the token (\n will not be added to token)
            # because it can only occur in whitespace or comment or error, the first 2 does not matter, while in the
            # third we don't want to have it in our error message
            if cur_char == '\n':
                linen += 1  # update line no
            else:
                token += cur_char
            cur_char = get_next_char()

        # here wi will handle the errors, we will raise Exception with appropriate error message
        # based on the current state we are in our dfa
        if next_node is None:
            if cur_node == 4:
                raise Exception("({}, Invalid number)".format(token))
            elif cur_node == 14:
                if token == "*/":
                    raise Exception("(*/, Unmatched comment)")
                else:
                    raise Exception("({}, Invalid input)".format(token))
            elif cur_node == 7 or cur_node == 8:
                raise Exception("({}..., Unclosed comment) ".format(token[:min(7, len(token))]))
            else:
                raise Exception("({}, Invalid input)".format(token))

        # we update current node with the next one
        cur_node = next_node[0]
        # and here , if we are in an accept node,
        # we are sure that we found a token and we will return the token with the appropriate token class
        # note that we do not have any transition which begins at an accept node
        if main_dfa.accept[cur_node]:
            if cur_node == 1 or cur_node == 3:  # we found a symbol !
                return "SYMBOL", token
            elif cur_node == 5:  # we found a num !
                return "NUM", token
            elif cur_node == 9:  # we found a comment !
                return "COMMENT", token
            elif cur_node == 12:  # we found an ID or KEYWORD !
                if token in KEYWORDS:
                    return "KEYWORD", token
                else:
                    return "ID", token
            elif cur_node == 13:  # we found WHITESPACE !
                return "WHITESPACE", token


# and we will use this function to find out in which line we are, note that it should be called before calling the
# get_next_token because that func will update line number.
def get_line_num():
    return linen
