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


main_dfa = DFA(14,[1,3,5,9,12,13])
#Symbols
main_dfa.add_trans(0, 1,"[](){}+-*<;:,")
main_dfa.add_trans(0, 2, "=")
main_dfa.add_trans(2, 1, "=")
main_dfa.add_trans(2, 3, "0123456789/ \n\f\r\v\t"+string.ascii_lowercase + string.ascii_uppercase, False)
#Num
main_dfa.add_trans(0, 4, "0123456789")
main_dfa.add_trans(4, 4, "0123456789")
main_dfa.add_trans(4, 5, "[](){}+-*<;:,=/ \n\f\r\v\t", False) #without ID or Keyword
#comment
main_dfa.add_trans(0, 6, "/") 
main_dfa.add_trans(6, 7, "*")
main_dfa.add_trans(7, 7, "[](){}+-<;:,=0123456789/ \n\f\r\v\t" + string.ascii_lowercase + string.ascii_uppercase)
main_dfa.add_trans(6, 10, "/")
main_dfa.add_trans(10, 10, "[](){}+-*<;:,=0123456789/ \f\r\v\t" + string.ascii_lowercase + string.ascii_uppercase)
main_dfa.add_trans(10, 9, "\n\0") #and EOF
main_dfa.add_trans(7, 8, "*")
main_dfa.add_trans(8, 8, "*")
main_dfa.add_trans(8, 7, "[](){}+-<;:,=0123456789 \n\f\r\v\t" + string.ascii_lowercase + string.ascii_uppercase)
main_dfa.add_trans(8, 9, "/")
#ID & Keyword
main_dfa.add_trans(0, 11, string.ascii_lowercase + string.ascii_uppercase) 
main_dfa.add_trans(11, 11, "0123456789"+string.ascii_lowercase + string.ascii_uppercase)
main_dfa.add_trans(11, 12, "[](){}+-*<;:,=/ \n\f\r\v\t", False) 
#whitespaces
main_dfa.add_trans(0, 13, " \n\f\r\v\t")    
