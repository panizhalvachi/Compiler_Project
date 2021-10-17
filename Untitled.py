from scanner import get_next_token, get_line_num

symbol_table_file = open("symbol_table.txt", "w")
symbol_set = set()

answer = dict()
while True:

    res = get_next_token()
    
    if res[0]=="ID":
    if res[1] not in symbol_set:
        symbol_set.add(res[1])
        symbol_table_file.write(res[1]+"\n")
    
    if res is None:
        break
    if res[0] in ("COMMENT", "WHITESPACE"):
        continue

    linen = get_line_num()
    if linen not in answer:
        answer[linen] = []
    answer[linen].append(res)

for key in answer:
    print("{}. ".format(key), end='')
    for (tp, lexeme) in answer[key]:
        print("({}, {}) ".format(tp, lexeme), end='')
    print()
symbol_table_file.close()
