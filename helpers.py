def _format_labels(labels):
    s = set(l.line_label for l in labels)
    s = '{' + ', '.join(s) + '}'
    return 'labels=' + s


def print_instructions(instructions):
    for i, instr in enumerate(instructions):
        if instr.func_name is not None:
            func_name = instr.func_name
            if not instr.has_labels():
                print(i, instr.data, '#', func_name)
            else:
                print(i, instr.data, '#', func_name, _format_labels(instr._labels))
        else:
            if not instr.has_labels():
                print(i, instr.data)
            else:
                print(i, instr.data, '#', _format_labels(instr._labels))
