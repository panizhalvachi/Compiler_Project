#!/usr/bin/env python
# coding: utf-8

# In[28]:


from scanner import get_next_token, get_line_num

symbol_table_file = open("symbol_table.txt", "w")
errors_file = open("lexical_errors.txt", "w")
tokens_file = open("tokens.txt", "w")
symbol_set = set()

KEYWORDS = ["if", "else", "void", "int", "repeat", "break", "until", "return"]
x = 1
answer = dict()
for keyword in KEYWORDS:
    symbol_table_file.write("{}.	{}".format(x,keyword)+"\n")
    x = x+1
while True:
    try:
        res = get_next_token()
        if res is None:
            break
        if res[0]=="ID":
            if res[1] not in symbol_set:
                symbol_set.add(res[1])
                symbol_table_file.write("{}.	{}".format(x,res[1])+"\n")
                x=x+1

        if res[0] in ("COMMENT", "WHITESPACE"):
            continue
    except Exception as error_msg:
        errors_file.write("{}.	{}".format(get_line_num(),str(error_msg))+"\n")
    


    linen = get_line_num()
    if linen not in answer:
        answer[linen] = []
    answer[linen].append(res)

for key in answer:
    tokens_file.write("{}. ".format(key)+" ")
    for (tp, lexeme) in answer[key]:
        tokens_file.write("({}, {}) ".format(tp, lexeme))
    tokens_file.write("\n")

symbol_table_file.close()
errors_file.close()
tokens_file.close()
