# Mehrshad Mirmohammad 98109634
# Paniz Halvachi 98109729

import anytree

import code_gen
import scanner
import semantic_checks
from first_follow import first_sets, follow_sets, none_terminals

nodes_adj = []

# we open action table file which is another way of showing transition diagrams
action_table_path = "actionsTable.txt"
action_table_stream = open(action_table_path, 'r').readlines()

# here we add adjacent nodes and edges for each node, based on action table, to nodes_adj.
for node_num, desc in enumerate(action_table_stream):
    desc = desc.split()[1:]
    # if the node shows an accept state (does not have any adjacent nodes) we add None to nodes_adj
    if len(desc) == 1:
        nodes_adj.append(None)
        continue
    nodes_adj.append([(desc[i], int(desc[i + 1])) for i in range(0, len(desc), 2)])

# we open nonTerminalsFirstState file. Starting state of each Non_Terminal is written in this file.
first_node = {}
none_terminal_first_node_path = "nonTerminalsFirstState.txt"
none_terminal_first_node_stream = open(none_terminal_first_node_path, 'r').readlines()

# store starting state of each Non_Terminal in first_node
for desc in none_terminal_first_node_stream:
    nt, first = desc.split()
    first_node[nt] = int(first)


# this function call get_next_token() method of scanner and returns number of the token's line and token
def get_next_token():
    linen, token = None, None
    while True:
        linen = scanner.get_line_num()  # save line number
        try:  # try to get the next token
            res = scanner.get_next_token()
            if res is None:  # if token is none (which should mean EOF) break the while loop
                break
            if res[0] in ("COMMENT", "WHITESPACE"):  # if token is white space, ignore it
                continue
            token = res
            break
        except Exception as error_msg:  # if an Exception occurred, add the error message to errors_list
            # add_to_dict(errors_list, linen, error_msg)
            # print(error_msg)
            continue
    if token is None:
        raise Exception("EOF reached without termination correctly :(")

    return linen, token


# store the given token in cur_line_token
cur_line_token = get_next_token()

root = None
syntax_errors_list = []


# the main method
def parse(node, par):
    global cur_line_token, root, syntax_errors_list
    # if node is a terminal then we convert it to the appropriate format. after that we add it as a child of par to
    # our parse tree.
    if node not in none_terminals:

        pre = cur_line_token[1]
        if node != 'epsilon' and pre != '$':
            cur_line_token = get_next_token()
        # appropriate format for epsilon is epsilon    
        if node == 'epsilon':
            s = 'epsilon'
        # appropriate format for $ is $     
        elif pre == '$':
            s = '$'
        # appropriate format for others is (token class, lexeme)    
        else:
            s = "({}, {})".format(pre[0], pre[1])

        return anytree.Node(s, parent=par)

    cur_any_node = anytree.Node(node, parent=par)
    if root is None:
        root = cur_any_node

    cur_node = first_node[node]
    code_gen.code_gen_node(cur_node, cur_line_token[0])

    while nodes_adj[cur_node] is not None:
        token = cur_line_token[1][0]
        # we consider lexeme as a token for 'symbol' and 'keyword' token classes and for others like 'ID' and et cetera
        if cur_line_token[1][0] in ('SYMBOL', 'KEYWORD'):
            token = cur_line_token[1][1]

        # the parser is in diagram A, the current token is a. the valid transitions are: when A is non-terminal and a
        # is a member of first-set(A) when A is non-terminal, epsilon is a member of first-set(A), and a is a member
        # of follow-set(A) when A is terminal and a == A when A is terminal and a == epsilon note: we can have more
        # than one transition for a state so we check all the possible adjacent nodes but if we encounter case 1 and
        # 2 for any adjacent nodes, then we stop checking the others.
        next_node, next_trans_token = None, None
        for trans_token, trans_node in nodes_adj[cur_node]:
            if trans_token in none_terminals and token in first_sets[trans_token]:
                next_node, next_trans_token = trans_node, trans_token
                break
            if trans_token not in none_terminals and token == trans_token:
                next_node, next_trans_token = trans_node, trans_token
                break
            if trans_token in none_terminals and 'epsilon' in first_sets[trans_token] and token in follow_sets[
                trans_token]:
                next_node, next_trans_token = trans_node, trans_token
            if trans_token not in none_terminals and 'epsilon' == trans_token:
                next_node, next_trans_token = trans_node, trans_token

        # set current node to next node and resume the process
        if next_node is not None:
            code_gen.code_gen_edge(cur_node, next_node, cur_line_token[1], cur_line_token[0], "start")
            parse(next_trans_token, cur_any_node)
            code_gen.code_gen_edge(cur_node, next_node, cur_line_token[1], cur_line_token[0], "end")
            cur_node = next_node
            code_gen.code_gen_node(cur_node, cur_line_token[0])
            continue

        raise Exception("there is a syntax error !")

    return cur_any_node


def parser():
    global root, syntax_errors_list

    parse('Program', None)

    code_gen.flush_outputs()
