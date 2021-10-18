import string
from typing import List


class DFA:
    def __init__(self, num_states: int, acc_states: List[int]):
        self.num_states = num_states
        self.trans = [[] for i in range(num_states)]
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


main_dfa = DFA(15, [1, 3, 5, 9, 12, 13])

digit = "0123456789"
sym = "[](){}+-*<;:,="
whitespace = " \n\f\r\v\t"
lower = string.ascii_lowercase
upper = string.ascii_uppercase

# Symbols
main_dfa.add_trans(0, 14, "*")
main_dfa.add_trans(14, 1, sym + digit + whitespace + lower + upper, False)
main_dfa.add_trans(0, 1, "[](){}+-<;:,")
main_dfa.add_trans(0, 2, "=")
main_dfa.add_trans(2, 1, "=")
main_dfa.add_trans(2, 3, "/\0" + digit + whitespace + lower + upper, False)
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

KEYWORDS = ["if", "else", "void", "int", "repeat", "break", "until", "return"]

linen = 1
input_path = "input.txt"
input_stream = open(input_path, 'r')

EOF = False


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


cur_char = get_next_char()


def get_next_token():
    global linen, cur_char
    cur_node = 0
    token = ""

    if cur_char == '\0':
        return None

    while True:
        if cur_char is None:
            # TODO: handle EOF
            # print("Oh no EOF and I dont know what to do !")
            return None
            pass

        next_node = main_dfa.next_state(cur_node, cur_char)

        if next_node is None or next_node[1] is True:

            if cur_char == '\n':
                linen += 1
            else:
                token += cur_char
            cur_char = get_next_char()

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

        cur_node = next_node[0]
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
            elif cur_node == 13:  # we found WHITESPACE
                return "WHITESPACE", token
            pass


def get_line_num():
    return linen
