from scanner import get_next_token, get_line_num

symbol_table_file = open("symbol_table.txt", "w")
errors_file = open("lexical_errors.txt", "w")
symbol_set = set()

answer = dict()
while True:
    try:
        res = get_next_token()
    except Exception as error_msg:
        errors_file.write(error_msg+"\n")
    
    if res is None:
        break
        
    if res[0]=="ID":
        if res[1] not in symbol_set:
            symbol_set.add(res[1])
            symbol_table_file.write(res[1]+"\n")
            

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
errors_file.close()
