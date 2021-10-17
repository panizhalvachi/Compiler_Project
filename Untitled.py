from scanner import get_next_token, get_line_num


answer = dict()
while True:

    res = get_next_token()
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
