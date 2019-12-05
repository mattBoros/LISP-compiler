from copy import deepcopy

from compile import Instruction
from parse import AST


def _is_deterministic_function(func_ast):
    # TODO: this might have to change
    # right now every function is deterministic
    # cause theres no random functions are anything
    return True


def _get_calls_in_function_ast(func_ast):
    if type(func_ast) == AST and func_ast.tokens[0] == 'if':
        assert len(func_ast.tokens) == 5
        calls = set()
        # 1, 2, 4, 5
        for index in [1, 2, 4]:
            calls.update(_get_calls_in_function_ast(func_ast.tokens[index]))
        return calls
    elif type(func_ast) == AST:
        calls = set()
        function = func_ast.tokens[0]
        calls.add(function)
        for arg in func_ast.tokens[1:]:
            calls.update(_get_calls_in_function_ast(arg))
        return calls
    else:
        return set()


def get_call_graph(function_asts):
    node_to_neighbors = {}
    for func_ast in function_asts:
        func_name = func_ast.tokens[0]
        calls = _get_calls_in_function_ast(func_ast.tokens[2])
        node_to_neighbors[func_name] = calls
    return node_to_neighbors


def optimize_function_ast(func_ast):
    return func_ast


def instructions_equal(i1, i2):
    return len(i1) == len(i2) and all(ii1 == ii2 for (ii1, ii2) in zip(i1, i2))


def _optimize_instructions_helper(instructions):
    instructions = deepcopy(instructions)

    for i in range(len(instructions)-1):
        i1 = instructions[i]
        i2 = instructions[i+1]

        # if there are two add-consts in a row, we combine them
        if len(i1) > 0 and len(i2) > 0 and i1[0] == i2[0] == 'add-const' and not i1.has_labels() and not i2.has_labels():
            assert i1.func_name is None or i2.func_name is None
            func_name = None
            if i1.func_name is not None:
                func_name = i1.func_name
            if i2.func_name is not None:
                func_name = i2.func_name

            new_instructions = []
            new_instructions.extend(instructions[:i])

            new_instr = Instruction(['add-const'] + i1[1:] + i2[1:], func_name=func_name)
            new_instructions.append(new_instr)

            new_instructions.extend(instructions[i+2:])
            return new_instructions

        # get rid of blank instructions
        if len(i1) == 0 and (i1.func_name is None or i2.func_name is None):
            func_name = None
            if i1.func_name is not None:
                func_name = i1.func_name
            if i2.func_name is not None:
                func_name = i2.func_name

            new_instructions = []
            new_instructions.extend(instructions[:i])

            labels = set(i1._labels)
            labels.update(i2._labels)
            new_instr = Instruction(i2.data, label=None, func_name=func_name)
            new_instr._labels = labels
            new_instructions.append(new_instr)

            new_instructions.extend(instructions[i + 2:])
            return new_instructions

        # if theres a jump that jumps to the next instruction, get rid of it
        if len(i1) > 0 and i1[0] == 'jump' and i1[1] in i2._labels and (i1.func_name is None or i2.func_name is None):
            func_name = None
            if i1.func_name is not None:
                func_name = i1.func_name
            if i2.func_name is not None:
                func_name = i2.func_name

            new_instructions = []
            new_instructions.extend(instructions[:i])

            labels = set(i1._labels)
            labels.update(i2._labels)
            new_instr = Instruction(i2.data, label=None, func_name=func_name)
            new_instr._labels = labels
            new_instructions.append(new_instr)

            new_instructions.extend(instructions[i + 2:])
            return new_instructions

    return instructions


def optimize_instructions(instructions):
    while True:
        new_instructions = _optimize_instructions_helper(instructions)
        if instructions == new_instructions:
            return instructions
        instructions = new_instructions
