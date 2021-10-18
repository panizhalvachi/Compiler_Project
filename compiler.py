#!/usr/bin/env python
# coding: utf-8

# In[28]:


from scanner import get_next_token, get_line_num, KEYWORDS

symbol_table_file = open("symbol_table.txt", "w")
errors_file = open("lexical_errors.txt", "w")
tokens_file = open("tokens.txt", "w")
symbol_set = set()
tokens_list = dict()
errors_list = dict()


def write_symbol_table(token):
    global symbol_set
    if token not in symbol_set:
        symbol_set.add(token)
        symbol_table_file.write("{}.	{}".format(len(symbol_set), token) + "\n")


def add_to_dict(d, linen, s):
    if linen not in d:
        d[linen] = []
    d[linen].append(s)


def write_from_dict_to_file(d, file):
    for key in d:
        file.write("{}.	".format(key))
        for s in d[key]:
            file.write("{} ".format(s))
        file.write("\n")


for keyword in KEYWORDS:
    write_symbol_table(keyword)

while True:
    linen = get_line_num()
    try:
        res = get_next_token()
        if res is None:
            break
        if res[0] == "ID":
            write_symbol_table(res[1])
        if res[0] in ("COMMENT", "WHITESPACE"):
            continue
    except Exception as error_msg:
        add_to_dict(errors_list, linen, error_msg)
        continue

    add_to_dict(tokens_list, linen, "({}, {})".format(res[0], res[1]))

write_from_dict_to_file(tokens_list, tokens_file)
if len(errors_list):
    write_from_dict_to_file(errors_list, errors_file)
else:
    errors_file.write("There is no lexical error.");

symbol_table_file.close()
errors_file.close()
tokens_file.close()
