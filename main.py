import time

from compile import compile_ast
from optimize import optimize_instructions, optimize_function_ast, get_call_graph
from helpers import print_instructions
from execute import execute_instructions, Stack, LinkedList
from parse import get_func_ast

source = [
#     '''
#     (fact (n)
#           [if (<= n 1) 1
#            else (* n (fact (+ n -1)))])
#     ''',
#
#     '''
#     (add-five (l)
#               [if (empty? l) l
#                else (cons (+ 5 (first l))
#                           (add-five (rest l)))])
#     ''',
#
#     '''
#     (max (l)
#          [if (empty? l) -1
#           else (max2 (first l) (max (rest l)))])
#     ''',
#
#     '''
# (max2 (a b)
#      [if (>= a b) a
#       else b])
# ''',
#
#     '''
#     (min2 (a b)
#     [if (<= a b) a
#      else b])
#     ''',

    '''
    (sum (l)
         [if (empty? l) 0
          else (+ (sum (rest l)) (first l))])
    ''',

]

function_asts = [get_func_ast(code) for code in source]
print('CALL GRAPH')
for key, value in get_call_graph(function_asts).items():
    print(key, ':', value)
function_asts = [optimize_function_ast(ast) for ast in function_asts]
instructions = compile_ast(function_asts)

print('\nORIGINAL INSTRUCTIONS')
print_instructions(instructions)


print('\nOPTIMIZED INSTRUCTIONS')
instructions = optimize_instructions(instructions)
print_instructions(instructions)





upper_limit = 100000
stack = Stack()
stack.add_to_top(-1)
stack.add_to_top(LinkedList.range(upper_limit))
# stack.add_to_top(5)
# stack.add_to_top(10000)

t1 = time.time()
stack, max_stack_length, instructions_run = execute_instructions(instructions, stack)
t2 = time.time()

print('\nRESULTS')
print('time taken :', t2 - t1)
print('max stack length :', max_stack_length)
print('instructions run :', instructions_run)
print('sum :', stack[0])