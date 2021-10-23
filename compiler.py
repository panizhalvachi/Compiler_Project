# Mehrshad Mirmohammad 98109634
# Paniz Halvachi 98109729

from scanner import get_next_token, get_line_num, KEYWORDS

symbol_table_file = open("symbol_table.txt", "w")
errors_file = open("lexical_errors.txt", "w")
tokens_file = open("tokens.txt", "w")
symbol_set = set()
tokens_list = dict()
errors_list = dict()


# this func will will check and write a token in the symbol table if it is new
def write_symbol_table(token):
    global symbol_set
    if token not in symbol_set:
        symbol_set.add(token)
        symbol_table_file.write("{}.	{}".format(len(symbol_set), token) + "\n")


# we use a dict to map errors and others things to the line number that they occur
# this func will add a string s with line_number to dict d
def add_to_dict(d, line_number, s):
    if line_number not in d:
        d[line_number] = []
    d[line_number].append(s)


# this func will write the contents of a dict in the file in a special format
def write_from_dict_to_file(d, file):
    for key in d:
        file.write("{}.	".format(key))
        for s in d[key]:
            file.write("{} ".format(s))
        file.write("\n")


# add keywords to symbol_table
for keyword in KEYWORDS:
    write_symbol_table(keyword)


while True:
    linen = get_line_num()  # save line number
    try:  # try to get the next token
        res = get_next_token()
        if res is None:  # if token is none (which should mean EOF) break the while loop
            break
        if res[0] == "ID":  # if token is ID then add it to the symbol table
            write_symbol_table(res[1])
        if res[0] in ("COMMENT", "WHITESPACE"):  # if token is white space, ignore it
            continue
    except Exception as error_msg:  # if an Exception occurred, add the error message to errors_list
        add_to_dict(errors_list, linen, error_msg)
        continue

    add_to_dict(tokens_list, linen, "({}, {})".format(res[0], res[1]))  # add the token to the tokens_list


# write the tokens in the file
write_from_dict_to_file(tokens_list, tokens_file)

# write errors in the lexical_errors.txt
if len(errors_list):
    write_from_dict_to_file(errors_list, errors_file)
else:
    errors_file.write("There is no lexical error.")

symbol_table_file.close()
errors_file.close()
tokens_file.close()
