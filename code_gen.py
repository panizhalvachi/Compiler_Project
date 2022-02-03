import semantic_checks

generated_code = []

global_section = 5000
stack_section = 10000
global_section_ptr = global_section


def variable_interpret(var, i, stay_with_address=False):
    assert var[1] not in ['#@', '@#']
    if '$' in var[1]:
        generated_code.append(["ADD",
                               runtime_address_stack_frame[2],
                               '#{}'.format(var[2]),
                               reserved_global_vars[i][2]
                               ])
        if '@' in var[1]:
            generated_code.append(["ASSIGN",
                                   '@{}'.format(reserved_global_vars[i][2]),
                                   reserved_global_vars[i][2]
                                   ])
        if stay_with_address is False:
            return '@{}'.format(reserved_global_vars[i][2])
        return reserved_global_vars[i][2]
    return var[1] + str(var[2])


def interpret_code(code):
    code = code.copy()
    gen_code = [code[0]]
    for i in range(1, len(code)):
        gen_code.append(variable_interpret(code[i], i - 1))
    generated_code.append(gen_code)


def get_new_global_address(sz=1):
    global global_section_ptr
    global_section_ptr += 4 * sz
    return global_section_ptr - 4 * sz


def get_new_global_tmp():
    address = get_new_global_address()
    interpret_code([
        'ASSIGN',
        ['', '#', stack_section],
        ['', '', address]
    ])
    return ["", "", address]


runtime_address_stack_ptr = get_new_global_tmp()
runtime_address_stack_frame = get_new_global_tmp()
reserved_global_vars = [get_new_global_tmp() for i in range(4)]

generated_code.append(['JP'])
main_starter_jump = len(generated_code) - 1


def load_action_symbols(file_path="action_symbols.txt"):
    node_actions = {}
    edge_actions = {}

    stream = open(file_path, 'r').readlines()
    for desc in stream:
        desc = desc.split()
        if len(desc) == 2:
            node_actions[int(desc[1])] = desc[0]
        else:
            if len(desc) == 3:
                desc.append('start')
            edge_actions[(int(desc[1]), int(desc[2]), desc[3])] = desc[0]

    return node_actions, edge_actions


node_actions, edge_actions = load_action_symbols()


def code_gen_node(node, line_n):
    # # print(node)
    if node in node_actions:
        # print(node)
        code_gen(node_actions[node], None, line_n)


def code_gen_edge(snode, dnode, token, line_n, tp='start'):
    if token != '$':
        token = token[1]
    if (snode, dnode, tp) in edge_actions:
        # print(snode, dnode, tp)
        code_gen(edge_actions[(snode, dnode, tp)], token, line_n)


stack = []
global_action_table = {}
local_action_table = {}
local_function_name = None
runtime_stack_ptr = 0
saved_stack_frame = None
repeat = []

function_call_args = []


def get_new_stack_address(sz=1):
    global runtime_stack_ptr
    assert runtime_stack_ptr is not None
    # interpret_code([
    #     'ADD',
    #     ['', '#', 4 * sz],
    #     runtime_address_stack_ptr,
    #     runtime_address_stack_ptr
    # ])
    runtime_stack_ptr += sz * 4
    return runtime_stack_ptr - 4 * sz


# not complete
def get_var(line_n, pid):
    if pid in local_action_table:
        return local_action_table[pid]
    elif pid in global_action_table:
        return global_action_table[pid]
    else:
        semantic_checks.scoping_error(line_n, pid)
        return [
            'NA', '', 0
        ]  # we return something meaningful enough to prevent errors ...


def get_new_stack_tmp():
    address = get_new_stack_address()
    return ["NA", "$", address]


# ['array', '$', 12]

def code_gen(routine_name, token, line_n):
    # print(routine_name, token, line_n)
    # generated_code.append(["++++++++++++++++++++++++", routine_name, token, line_n])
    global stack
    global global_action_table
    global local_action_table
    global local_function_name
    global runtime_stack_ptr
    global saved_stack_frame
    debug_mode = False
    debug_mode2 = False

    if routine_name == 'type_specifier':
        stack.append(token)
    elif routine_name == 'put_id':
        if local_function_name is None:
            global_action_table[token] = list()
        else:
            local_action_table[token] = list()
        stack.append(token)
    elif routine_name == 'none_array_declaration':
        pid = stack.pop()
        tp = stack.pop()
        semantic_checks.void_type_semantic_check(line_n, tp, pid)

        if pid in local_action_table:
            local_action_table[pid] = [tp, "$", get_new_stack_address()]
        else:
            global_action_table[pid] = [tp, "", get_new_global_address()]
    elif routine_name == 'array_declaration':
        pid = stack.pop()
        tp = stack.pop()
        semantic_checks.void_type_semantic_check(line_n, tp, pid)

        if pid in local_action_table:
            address = get_new_stack_address(int(token))
            tmp = get_new_stack_tmp()
            generated_code.append([
                'ASSIGN',
                variable_interpret(['', '$', address], 1, stay_with_address=True),
                variable_interpret(tmp, 2)
            ])
            local_action_table[pid] = ["array", "$", tmp[2]]
        else:
            address = get_new_global_address(int(token))
            global_action_table[pid] = ["array", "#", address]
    elif routine_name == 'fun_declaration':
        fname = stack.pop()
        return_tp = stack.pop()

        global_action_table[fname] = {'name':fname, 'return_type': return_tp, 'param': [], 'address': len(generated_code)}
        local_function_name = fname
        runtime_stack_ptr = 8  # first 8 bytes are reserved for return value and stack
        if debug_mode:
            generated_code.append(['PRINT', 5000])
            generated_code.append(['PRINT', 5004])
    elif routine_name == 'fun_declaration_end':
        code_gen('return_void', None, line_n)
        local_action_table = {}
        local_function_name = None
        runtime_stack_ptr = 0
    elif routine_name == 'param_type_array':
        pid = stack.pop()
        tp = stack.pop()
        semantic_checks.void_type_semantic_check(line_n, tp, pid)

        local_action_table[pid] = ["array", "$", runtime_stack_ptr]
        runtime_stack_ptr += 4
        global_action_table[local_function_name]['param'].append('array')
    elif routine_name == 'param_type_n_array':
        pid = stack.pop()
        tp = stack.pop()
        semantic_checks.void_type_semantic_check(line_n, tp, pid)

        local_action_table[pid] = [tp, "$", runtime_stack_ptr]
        runtime_stack_ptr += 4
        global_action_table[local_function_name]['param'].append(tp)
    elif routine_name == 'main_starter':
        generated_code[main_starter_jump].append(len(generated_code))
        code_gen('pid', 'main', -2)
        code_gen('start_args', None, -2)
        code_gen('call_function', None, -2)
    elif routine_name == "save_stack_frame":
        saved_stack_frame = runtime_stack_ptr
        interpret_code(["ASSIGN",
                        runtime_address_stack_frame,
                        ['', '@', runtime_address_stack_ptr[2]]])
        interpret_code(["ASSIGN", runtime_address_stack_ptr, runtime_address_stack_frame])
        interpret_code(["SUB",
                        runtime_address_stack_frame,
                        ['', '#', runtime_stack_ptr],
                        runtime_address_stack_frame])
        get_new_stack_tmp()
    elif routine_name == 'do_operation':
        tmp = get_new_stack_tmp()
        # print(stack[-3:])
        res = semantic_checks.type_mismatch_check(stack[-1][0], stack[-3][0], line_n)
        interpret_code([
            stack[-2],
            stack[-3],
            stack[-1],
            tmp
        ])
        tmp[0] = res
        stack.pop()
        stack.pop()
        stack.pop()
        stack.append(tmp)
    elif routine_name == 'save_operation':
        if token == '+':
            stack.append('ADD')
        elif token == '-':
            stack.append('SUB')
        elif token == '*':
            stack.append('MULT')
        elif token == '==':
            stack.append('EQ')
        elif token == '<':
            stack.append('LT')
    elif routine_name == 'pid':
        stack.append(get_var(line_n, token))
    elif routine_name == 'array_index':
        tmp = get_new_stack_tmp()
        interpret_code([
            'ADD',
            stack[-1],
            stack[-2],
            tmp
        ])
        # tmp2 = get_new_stack_tmp()
        # tmp[1] += '@'
        # interpret_code([
        #     'ASSIGN',
        #     tmp,
        #     tmp2
        # ])
        stack.pop()
        stack.pop()
        # stack.append(tmp2)
        stack.append(['int', '@$', tmp[2]])
    elif routine_name == 'assign':
        interpret_code([
            'ASSIGN',
            stack[-1],
            stack[-2]
        ])
        stack.pop()
    elif routine_name == 'push':
        stack.append(['int', '#', str(token)])
    elif routine_name == 'start_args':
        function_call_args.append([])
    elif routine_name == 'fill_record':
        function_call_args[-1].append(stack.pop())
    elif routine_name == 'call_function':
        f = stack.pop()
        # print(f)
        args = function_call_args.pop()
        semantic_checks.args_check(f['param'], args, f['name'], line_n)

        return_value = get_new_stack_tmp()  # stack_frame

        tmp2 = runtime_stack_ptr

        return_address = get_new_stack_tmp()
        for arg in args:
            tmp = get_new_stack_tmp()
            # print("-----------", arg, tmp)
            interpret_code([
                'ASSIGN',
                arg,
                tmp
            ])
        interpret_code([
            'ADD',
            ['', '#', runtime_stack_ptr],
            runtime_address_stack_frame,
            runtime_address_stack_ptr
        ])
        interpret_code([
            'ASSIGN',
            ['', '', 0],
            return_address
        ])
        generated_code[-1][1] = '#{}'.format(len(generated_code) + 1)
        interpret_code([
            'JP',
            ['', '', f['address']]
        ])
        return_value[0] = f['return_type']
        stack.append(return_value)
        runtime_stack_ptr = tmp2
    elif routine_name == 'return_void':
        interpret_code([
            'ADD',
            runtime_address_stack_frame,
            ['', '#', 4],
            runtime_address_stack_ptr
        ])
        interpret_code([
            'ASSIGN',
            ['', '$', 4],
            reserved_global_vars[3]
        ])
        interpret_code(["ASSIGN",
                        ['', '$', saved_stack_frame],
                        runtime_address_stack_frame
                        ])
        if debug_mode:
            generated_code.append(['PRINT', 5000])
            generated_code.append(['PRINT', 5004])
        interpret_code([
            'JP',
            ['', '@', reserved_global_vars[3][2]]
        ])
    elif routine_name == 'return_value':
        interpret_code([
            'ASSIGN',
            stack.pop(),
            ['', '$', 0]
        ])
        interpret_code([
            'ADD',
            runtime_address_stack_frame,
            ['', '#', 4],
            runtime_address_stack_ptr
        ])
        interpret_code([
            'ASSIGN',
            ['', '$', 4],
            reserved_global_vars[3]
        ])
        interpret_code(["ASSIGN",
                        ['', '$', saved_stack_frame],
                        runtime_address_stack_frame
                        ])
        if debug_mode:
            generated_code.append(['PRINT', 5000])
            generated_code.append(['PRINT', 5004])
        interpret_code([
            'JP',
            ['', '@', reserved_global_vars[3][2]]
        ])
    elif routine_name == 'pop':
        stack.pop()
    elif routine_name == 'save_break':
        interpret_code([
            "JP",
            ['', '', 0],
        ])
        if len(repeat) == 0:
            semantic_checks.break_semantic_error(line_n)
        else:
            repeat[-1].append(len(generated_code) - 1)
    elif routine_name == 'save_if':
        interpret_code([
            "JPF",
            stack.pop(),  # stack(top)
            ['', '', 0],
        ])
        stack.append(['', '', len(generated_code) - 1])
    elif routine_name == 'jpf':
        generated_code[stack.pop()[2]][2] = (len(generated_code))
    elif routine_name == 'jpf_save':
        generated_code[stack.pop()[2]][2] = len(generated_code) + 1  # i+1
        interpret_code([
            "JP",
            ['', '', 0],
        ])
        stack.append(['', '', len(generated_code) - 1])
    elif routine_name == 'jp':
        generated_code[stack.pop()[2]][1] = len(generated_code)
    elif routine_name == 'label':
        stack.append(['', '', len(generated_code)])
        repeat.append([])
    elif routine_name == 'until':
        # print(stack[-2:])
        interpret_code([
            "JPF",
            stack.pop(),
            stack.pop(),
        ])
        for br in repeat[-1]:
            generated_code[br][1] = len(generated_code)
    else:
        raise Exception("no such action symbol in code_gen()!")

    if debug_mode2:
        generated_code.append(["-------------------------{}".format(runtime_stack_ptr), routine_name, token, line_n])


def flush_outputs():
    semantic_errors_list = semantic_checks.get_errors_list()

    semantic_errors_file = open("semantic_errors.txt", 'w')
    output_file = open("output.txt", 'w')

    if len(semantic_errors_list) > 0:
        output_file.write('The code has not been generated.\n')
        for err in semantic_errors_list:
            semantic_errors_file.write(err + '\n')
    else:
        semantic_errors_file.write('The input program is semantically correct.\n')
        i = 0
        for code in generated_code:
            while len(code) < 4:
                code.append('')
            output_file.write("{}\t({}, {}, {}, {})\n".format(i, code[0], code[1], code[2], code[3]))
            if code[0][0] not in '-+':
                i += 1

    semantic_errors_file.close()
    output_file.close()


#####################################################################################################################

code_gen('type_specifier', 'void', -1)
code_gen('put_id', 'output', -1)
code_gen('fun_declaration', None, -1)
code_gen('type_specifier', 'int', -1)
code_gen('put_id', 'a', -1)
code_gen('param_type_n_array', None, -1)
code_gen('save_stack_frame', None, -1)
interpret_code([
    'PRINT',
    get_var(-1, 'a')
])
code_gen('fun_declaration_end', None, -1)

#####################################################################################################################