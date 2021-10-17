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


main_dfa = DFA(14, [1, 3, 5, 9, 12, 13])
# Symbols
main_dfa.add_trans(0, 1, "[](){}+-*<;:,")
main_dfa.add_trans(0, 2, "=")
main_dfa.add_trans(2, 1, "=")
main_dfa.add_trans(2, 3, "0123456789/ \n\f\r\v\t" + string.ascii_lowercase + string.ascii_uppercase, False)
# Num
main_dfa.add_trans(0, 4, "0123456789")
main_dfa.add_trans(4, 4, "0123456789")
main_dfa.add_trans(4, 5, "[](){}+-*<;:,=/ \n\f\r\v\t", False)  # without ID or Keyword
# comment
main_dfa.add_trans(0, 6, "/")
main_dfa.add_trans(6, 7, "*")
main_dfa.add_trans(7, 7, "[](){}+-<;:,=0123456789/ \n\f\r\v\t" + string.ascii_lowercase + string.ascii_uppercase)
main_dfa.add_trans(6, 10, "/")
main_dfa.add_trans(10, 10, "[](){}+-*<;:,=0123456789/ \f\r\v\t" + string.ascii_lowercase + string.ascii_uppercase)
main_dfa.add_trans(10, 9, "\n\0")  # and EOF
main_dfa.add_trans(7, 8, "*")
main_dfa.add_trans(8, 8, "*")
main_dfa.add_trans(8, 7, "[](){}+-<;:,=0123456789 \n\f\r\v\t" + string.ascii_lowercase + string.ascii_uppercase)
main_dfa.add_trans(8, 9, "/")
# ID & Keyword
main_dfa.add_trans(0, 11, string.ascii_lowercase + string.ascii_uppercase)
main_dfa.add_trans(11, 11, "0123456789" + string.ascii_lowercase + string.ascii_uppercase)
main_dfa.add_trans(11, 12, "[](){}+-*<;:,=/ \n\f\r\v\t", False)
# whitespaces
main_dfa.add_trans(0, 13, " \n\f\r\v\t")

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
            raise Exception("EOF reached, no more chars left!")
    return next_char


cur_char = get_next_char()


def get_next_token():
    global linen, cur_char
    cur_node = 0
    token = ""
    while True:
        if cur_char == '\0':
            # TODO: handle EOF
            # print("Oh no EOF and I dont know what to do !")
            return None
            pass
        next_node = main_dfa.next_state(cur_node, cur_char)
        if next_node is None:
            # TODO: handle stuck in a state
            # print("Oh no we got stuck in state {}".format(cur_node))
            return None

        if next_node[1]:
            token += cur_char
            if cur_char == '\n':
                linen += 1
            cur_char = get_next_char()
        cur_node = next_node[0]
        if main_dfa.accept[cur_node]:
            # TODO : different accept types
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
