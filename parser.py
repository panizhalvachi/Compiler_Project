import anytree

import scanner
from first_follow import first_sets, follow_sets, none_terminals

nodes_adj = []

action_table_path = "actionsTable.txt"
action_table_stream = open(action_table_path, 'r').readlines()

for node_num, desc in enumerate(action_table_stream):
    desc = desc.split()[1:]
    if len(desc) == 1:
        nodes_adj.append(None)
        continue

    nodes_adj.append([(desc[i], int(desc[i + 1])) for i in range(0, len(desc), 2)])

first_node = {}
none_terminal_first_node_path = "nonTerminalsFirstState.txt"
none_terminal_first_node_stream = open(none_terminal_first_node_path, 'r').readlines()

for desc in none_terminal_first_node_stream:
    nt, first = desc.split()
    first_node[nt] = int(first)


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


cur_line_token = get_next_token()

root = None


def parse(node, par):
    global cur_line_token, root
    if node not in none_terminals:
        pre = cur_line_token[1]
        if node != 'epsilon' and pre != '$':
            cur_line_token = get_next_token()

        if node == 'epsilon':
            s = node
        elif pre == '$':
            s = '$'
        else:
            s = "({}, {})".format(pre[0], pre[1])

        return anytree.Node(s, parent=par)

    cur_any_node = anytree.Node(node, parent=par)
    if root is None:
        root = cur_any_node

    cur_node = first_node[node]

    while nodes_adj[cur_node] is not None:
        token = cur_line_token[1][0]
        if cur_line_token[1][0] in ('SYMBOL', 'KEYWORD'):
            token = cur_line_token[1][1]
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

        if next_node is None:
            raise Exception("{} {} I dont know where to go :( line 72 parser".format(cur_node, token))

        parse(next_trans_token, cur_any_node)
        cur_node = next_node

    return cur_any_node


def parser():
    global root

    root = None
    parse('Program', None)

    parse_tree_file = open("parse_tree.txt", 'w')

    for pre, fill, node in anytree.RenderTree(root):
        parse_tree_file.write("%s%s\n" % (pre, node.name))

    parse_tree_file.close()


syntax_errors_file = open("syntax_errors.txt", 'w')
syntax_errors_list = []
