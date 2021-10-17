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
