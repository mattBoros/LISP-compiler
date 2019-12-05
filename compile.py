from parse import get_func_ast


class LabelCounter:
    labels = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    def __init__(self):
        self.max_label = -1
    def get_next_label(self):
        self.max_label += 1
        return self.labels[self.max_label]


class LineNumber:
    def __init__(self, line_number):
        self.line_number = line_number

    def __str__(self):
        return f'LineNumber({self.line_number})'

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.line_number == other.line_label


class LineLabel:
    def __init__(self, line_label):
        self.line_label = line_label

    def __str__(self):
        return f'LineLabel({self.line_label})'

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.line_label == other.line_label

    def __hash__(self):
        return hash(self.line_label)

class StackIndex:
    def __init__(self, stack_index):
        self.stack_index = stack_index

    def __str__(self):
        return f'StackIndex({self.stack_index})'

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.stack_index == other.stack_index


class Constant:
    def __init__(self, constant):
        self.constant = constant

    def __str__(self):
        return f'Constant({self.constant})'

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.constant == other.constant


class Instruction:
    __slots__ = ['data', '_labels', 'func_name']

    def __init__(self, data, label=None, func_name=None):
        self.data = data
        if label is None:
            self._labels = set()
        else:
            self._labels = {label}
        self.func_name = func_name

    def __eq__(self, other):
        return self.data == other.data and self._labels == other._labels and self.func_name == other.func_name

    def add_label(self, label):
        self._labels.add(label)

    def has_labels(self):
        return len(self._labels) > 0

    def __getitem__(self, item):
        return self.data[item]

    def append(self, value):
        self.data.append(value)

    def __len__(self):
        return len(self.data)


def add_to_dictionary_vals(d, v):
    for k in d:
        d[k] += v


def is_int(s):
    try:
        int(s)
        return True
    except:
        return False


def get_instructions(instructions, ast, arg_to_stack_index, label_counter):
    if type(ast) == str and  ast[0] not in ['(', '[']:
        index = arg_to_stack_index[ast]
        instructions.append(Instruction(['add-to-stack', StackIndex(index)]))

    elif ast.tokens[0] == 'if':
        assert len(ast.tokens) == 5 and ast.tokens[3] == 'else'
        cmp = ast.tokens[1]
        if type(cmp) == str:
            index = arg_to_stack_index[cmp]
            # instructions.append(f'add {index} to stack')
            instructions.append(Instruction(['add-to-stack', StackIndex(index)]))
        else:
            get_instructions(instructions, cmp, arg_to_stack_index, label_counter)
        add_to_dictionary_vals(arg_to_stack_index, 1)

        # instructions.append('cmp ')
        true_label = LineLabel(label_counter.get_next_label())
        false_label = LineLabel(label_counter.get_next_label())
        instructions.append(Instruction(['cmp', true_label, false_label]))
        add_to_dictionary_vals(arg_to_stack_index, -1)

        true_start_index = len(instructions)
        if is_int(ast.tokens[2]):
            # instructions.append('add const {} to stack'.format(ast.tokens[2]))
            constant = int(ast.tokens[2])
            instructions.append(Instruction(['add-const', Constant(constant)]))
        elif type(ast.tokens[2]) == str:
            index = arg_to_stack_index[ast.tokens[2]]
            instructions.append(Instruction(['add-to-stack', StackIndex(index)]))
        else:
            get_instructions(instructions, ast.tokens[2], arg_to_stack_index, label_counter)
        instructions[true_start_index].add_label(true_label)
        # instructions.append('jump to ')
        instructions.append(Instruction(['jump']))
        true_end_index = len(instructions)-1

        false_start_index = len(instructions)
        if is_int(ast.tokens[4]):
            # instructions.append('add const {} to stack'.format(ast.tokens[4]))
            constant = int(ast.tokens[4])
            instructions.append(Instruction(['add-const', Constant(constant)]))
        elif type(ast.tokens[4]) == str:
            index = arg_to_stack_index[ast.tokens[4]]
            instructions.append(Instruction(['add-to-stack', StackIndex(index)]))
        else:
            get_instructions(instructions, ast.tokens[4], arg_to_stack_index, label_counter)
        instructions[false_start_index].add_label(false_label)
        # instructions.append('jump to ')
        instructions.append(Instruction(['jump']))
        false_end_index = len(instructions)-1

        jump_location = len(instructions)
        jump_location_label = label_counter.get_next_label()
        instructions[true_end_index].append(LineLabel(jump_location_label))
        instructions[false_end_index].append(LineLabel(jump_location_label))
        instructions.append(Instruction([], label=LineLabel(jump_location_label)))
    else:
        # print('normal func call')
        func = ast.tokens[0]
        args = ast.tokens[1:]
        add_to_dictionary_vals(arg_to_stack_index, 1)
        add_const_index = len(instructions)
        instructions.append(Instruction(['add-const']))
        for arg in args:
            if type(arg) == str:
                if is_int(arg):
                    # new_instructions.append(f'add const {arg} to stack')
                    instructions.append(Instruction(['add-const', Constant(int(arg))]))
                else:
                    index = arg_to_stack_index[arg]
                    # new_instructions.append(f'add {index} to stack')
                    instructions.append(Instruction(['add-to-stack', StackIndex(index)]))
            else:
                get_instructions(instructions, arg, arg_to_stack_index, label_counter)
            add_to_dictionary_vals(arg_to_stack_index, 1)

        # instructions.append(f'add const {line_to_return} to stack')
        # instructions.append(f'func-call {func}')
        instructions.append(Instruction(['func-call', func]))
        return_index = len(instructions)
        return_label = label_counter.get_next_label()
        instructions.append(Instruction([], label=LineLabel(return_label)))
        instructions[add_const_index].append(LineLabel(return_label))
        add_to_dictionary_vals(arg_to_stack_index, -len(args)-1)


def compile_source(source):
    func_asts = [get_func_ast(code) for code in source]
    instructions = []
    for func_ast in func_asts:
        func_name = func_ast.tokens[0]
        func_index = len(instructions)
        args = func_ast.tokens[1].tokens
        func_def = func_ast.tokens[2]
        arg_to_stack_index = {arg: args.index(arg) for arg in args}

        get_instructions(instructions, func_def, arg_to_stack_index, LabelCounter())
        instructions.append(Instruction(['exit', Constant(len(args))]))
        instructions[func_index].func_name = func_name
    return instructions

