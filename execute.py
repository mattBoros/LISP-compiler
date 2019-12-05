from copy import deepcopy

from compile import LineLabel, Constant, LineNumber
from helpers import print_instructions



class LinkedList:
    def __init__(self, value, next):
        self.value = value
        self.next = next

    @staticmethod
    def range(maxval):
        node = None
        for i in reversed(range(maxval)):
            new_node = LinkedList(value=i, next=node)
            node = new_node
        return node

    def __str__(self):
        l = []
        node = self
        while node is not None:
            l.append(node.value)
            node = node.next
        return str(l)


class Stack:
    __slots__ = ['ll', 'length']

    def __init__(self):
        self.ll = None
        self.length = 0

    def add_to_top(self, v):
        self.length += 1
        node = LinkedList(v, self.ll)
        self.ll = node

    def pop(self, index):
        self.length -= 1
        if index == 0:
            val = self.ll.value
            self.ll = self.ll.next
            return val
        node = self.ll
        prev = None
        for i in range(index):
            prev = node
            node = node.next
        prev.next = node.next
        return node.value

    def __len__(self):
        return self.length

    def __getitem__(self, item):
        node = self.ll
        for i in range(item):
            node = node.next
        return node.value

    def __str__(self):
        l = []
        for i in range(len(self)):
            l.append(self[i])
        return str(l)


def _finalize_instructions(instructions):
    instructions = deepcopy(instructions)

    label_to_line_num = {}
    for line_num, instr in enumerate(instructions):
        if instr.has_labels():
            assert not any(label.line_label in label_to_line_num for label in instr._labels)
            for label in instr._labels:
                label_to_line_num[label.line_label] = line_num

    for i, instr in enumerate(instructions):
        for j, data in enumerate(instr.data):
            if type(data) == LineLabel:
                line_number = label_to_line_num[data.line_label]
                if instr[0] == 'add-const':
                    instr.data[j] = Constant(line_number)
                else:
                    instr.data[j] = LineNumber(line_number)

    func_to_instruction_num = {}
    for i, instr in enumerate(instructions):
        if instr.func_name is not None:
            func_to_instruction_num[instr.func_name] = i

    return instructions, func_to_instruction_num


def execute_instructions(instructions, stack):
    instructions, func_to_instruction_num = _finalize_instructions(instructions)
    print('\nFINAL INSTRUCTIONS')
    print_instructions(instructions)

    max_stack_length = -1
    instructions_run = 0

    line_num = 0
    while line_num != -1:
        # print('----')
        # if line_num in func_to_instruction_num.values():
        #     for func_name, line in func_to_instruction_num.items():
        #         if line == line_num:
        #             break
            # print(f'START OF {func_name.upper()} FUNCTION')
        # print(instructions[line_num].data)
        # print('instructions run :', instructions_run)
        # print('stack :', stack)
        max_stack_length = max(max_stack_length, len(stack))
        instructions_run += 1

        instr = instructions[line_num]
        if len(instr) == 0:
            line_num += 1
            continue
        instr_name = instr[0]

        if instr_name == 'add-const':
            for const in instr[1:]:
                stack.add_to_top(const.constant)
            line_num += 1
        elif instr_name == 'add-to-stack':
            stack_index = instr[1].stack_index
            stack.add_to_top(stack[stack_index])
            line_num += 1
        elif instr_name == 'func-call':
            func_name = instr[1]
            if func_name in func_to_instruction_num:
                line_num = func_to_instruction_num[func_name]
            elif func_name == 'empty?':
                l = stack.pop(0)
                line_num = stack.pop(0)
                if l is None:
                    res = 1
                else:
                    res = 0
                stack.add_to_top(res)
            elif func_name == 'first':
                l = stack.pop(0)
                line_num = stack.pop(0)
                stack.add_to_top(l.value)
            elif func_name == 'rest':
                l = stack.pop(0)
                line_num = stack.pop(0)
                stack.add_to_top(l.next)
            elif func_name == 'cons':
                linked_list = stack.pop(0)
                item = stack.pop(0)
                line_num = stack.pop(0)
                new_ll = LinkedList(value=item, next=linked_list)
                stack.add_to_top(new_ll)
            elif func_name == '+':
                arg1 = stack.pop(0)
                arg2 = stack.pop(0)
                line_to_return = stack.pop(0)
                stack.add_to_top(arg1 + arg2)
                line_num = line_to_return
            elif func_name == '*':
                arg1 = stack.pop(0)
                arg2 = stack.pop(0)
                line_to_return = stack.pop(0)
                stack.add_to_top(arg1 * arg2)
                line_num = line_to_return
            elif func_name == '==':
                arg1 = stack.pop(0)
                arg2 = stack.pop(0)
                line_to_return = stack.pop(0)
                if arg2 == arg1:
                    result = 1
                else:
                    result = 0
                stack.add_to_top(result)
                line_num = line_to_return
            elif func_name == '>=':
                arg1 = stack.pop(0)
                arg2 = stack.pop(0)
                line_to_return = stack.pop(0)
                if arg2 >= arg1:
                    result = 1
                else:
                    result = 0
                stack.add_to_top(result)
                line_num = line_to_return
            elif func_name == '<=':
                arg1 = stack.pop(0)
                arg2 = stack.pop(0)
                line_to_return = stack.pop(0)
                if arg2 <= arg1:
                    result = 1
                else:
                    result = 0
                stack.add_to_top(result)
                line_num = line_to_return
            elif func_name == '>':
                arg1 = stack.pop(0)
                arg2 = stack.pop(0)
                line_to_return = stack.pop(0)
                if arg2 > arg1:
                    result = 1
                else:
                    result = 0
                stack.add_to_top(result)
                line_num = line_to_return
            elif func_name == '<':
                arg1 = stack.pop(0)
                arg2 = stack.pop(0)
                line_to_return = stack.pop(0)
                if arg2 < arg1:
                    result = 1
                else:
                    result = 0
                stack.add_to_top(result)
                line_num = line_to_return
            else:
                raise Exception('unknown function', func_name)
        elif instr_name == 'cmp':
            top = stack.pop(0)
            true_index, false_index = instr[1:]
            if top == 1:
                line_num = true_index.line_number
            else:
                line_num = false_index.line_number
        elif instr_name == 'jump':
            line_num = instr[1].line_number
        elif instr_name == 'exit':
            num_args = instr[1].constant
            for i in range(num_args):
                stack.pop(1)
            line_num = stack.pop(1)
        else:
            raise Exception('unrecognized instruction', instr_name)

    return stack, max_stack_length, instructions_run