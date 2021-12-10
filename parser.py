# Mehrshad Mirmohammad 98109634
# Paniz Halvachi 98109729

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
syntax_errors_list = []


def parse(node, par):
    global cur_line_token, root, syntax_errors_list
    if node not in none_terminals:
        pre = cur_line_token[1]
        if node != 'epsilon' and pre != '$':
            cur_line_token = get_next_token()

        if node == 'epsilon':
            s = 'epsilon'
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

        if next_node is not None:
            parse(next_trans_token, cur_any_node)
            cur_node = next_node
            continue

        trans_token, trans_node = nodes_adj[cur_node][0]

        if trans_token in none_terminals and 'epsilon' not in first_sets[trans_token] and token in follow_sets[trans_token]:
            cur_node = trans_node  # check
            syntax_errors_list.append("#{} : syntax error, missing {}".format(cur_line_token[0], trans_token))

        elif trans_token in none_terminals:
            syntax_errors_list.append("#{} : syntax error, illegal {}".format(cur_line_token[0], token))
            cur_line_token = get_next_token()
            if cur_line_token[1] == '$':
                syntax_errors_list.append("#{} : syntax error, Unexpected EOF".format(cur_line_token[0]))
                raise Exception()
        else:
            cur_node = trans_node
            syntax_errors_list.append("#{} : syntax error, missing {}".format(cur_line_token[0], trans_token))

    return cur_any_node


def parser():
    global root, syntax_errors_list

    parse_tree_file = open("parse_tree.txt", 'w')
    syntax_errors_file = open("syntax_errors.txt", 'w')
    syntax_errors_list = []

    root = None
    try:
        parse('Program', None)
    except:
        pass

    if len(syntax_errors_list) == 0:
        syntax_errors_list.append('There is no syntax error.')

    for e in syntax_errors_list:
        syntax_errors_file.write(e + '\n')

    for pre, fill, node in anytree.RenderTree(root):
        parse_tree_file.write("%s%s\n" % (pre, node.name))

    parse_tree_file.close()
    syntax_errors_file.close()
