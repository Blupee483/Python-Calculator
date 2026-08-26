import math

def main():
    while True:
        print('Input "end" to end program')
        print('Input an equation to solve:')
        eq = input('~ ')

        if eq == 'end':
            break

        #debug
        if eq == 'default':
            eq = '10/-(5-3*2/(2^2-1)-1)+1.1+sin(pi/2)'
            print(eq)

        parsed_equation = parse_equation(eq)
        print('')
        print(f'{solve_equation(parsed_equation)}\n')

def solve_equation(parsed_equation):       
    print('-')
    print(parsed_equation)

    #find first set of paranthesis to solve
    open_idx = -1
    end_idx = len(parsed_equation)
    has_paranthesis = '(' in parsed_equation or ')' in parsed_equation
    if has_paranthesis:
        i = 0
        while parsed_equation[i] != ')':
            if i >= len(parsed_equation):
                parsed_equation += ')'
                break

            if parsed_equation[i] == '(':
                open_idx = i
            i += 1
        end_idx = i

    to_solve = parsed_equation[open_idx + 1:end_idx]

    print('To solve:')
    print(to_solve)

    #recurse if paranthesis contains a single number
    if len(to_solve) == 1 and has_paranthesis:
        parsed_equation.pop(end_idx)
        parsed_equation.pop(open_idx)
        return solve_equation(parsed_equation)
    elif len(to_solve) == 1 and not has_paranthesis:
        print('Equation solved')
        return parsed_equation[0]

    #finds an operator and a pair of numbers to solve
    def check_for_operation(parsed_equation, to_solve, operators):
        operator_found = False
        for i in range(len(to_solve)):
            if to_solve[i] in operators:
                operator_found = True

                num1 = to_solve[i - 1]
                num2 = to_solve[i + 1]
                val = perform_operation(num1, num2, to_solve[i])

                to_solve.pop(i + 1)
                to_solve.pop(i)
                to_solve.pop(i - 1)
                to_solve.insert(i-1, val)
                print(to_solve)

                del parsed_equation[open_idx+1:end_idx]
                parsed_equation[open_idx + 1:open_idx + 1] = to_solve

                return parsed_equation, operator_found

        return parsed_equation, operator_found

    #check for special functions: (sin, cos, tan, log, ln, etc)
    found = False
    func_idx = 0
    for i in range(len(parsed_equation)):
        if is_func(parsed_equation[i]):
            func_arg = parsed_equation[i+1]
            if type(func_arg) != type(1.0):
                continue

            func_name = parsed_equation[i]
            found = True

            val = perform_operation(func_arg, 0, func_name)
            parsed_equation.pop(i+1)
            parsed_equation.pop(i)
            parsed_equation.insert(i, val)

            print(f'function solved: {func_name}')
            print(parsed_equation)

            return solve_equation(parsed_equation)

    #check for ^
    parsed_equation, found = check_for_operation(parsed_equation, to_solve, ['^'])
    if found:
        return solve_equation(parsed_equation)

    #check for * or /
    parsed_equation, found = check_for_operation(parsed_equation, to_solve, ['*', '/'])
    if found:
        return solve_equation(parsed_equation)
    
    #check for + or -
    parsed_equation, found = check_for_operation(parsed_equation, to_solve, ['+', '-'])
    if found:
        return solve_equation(parsed_equation)
            
    return parsed_equation[0]

def perform_operation(n1, n2, operator):
    #standard operators
    match operator:
        case '+': return n1 + n2
        case '-': return n1 - n2
        case '*': return n1 * n2
        case '/': 
            if n2 == 0.0:
                raise ZeroDivisionError(f'Attempted zero division; Answer is undefined')
            return n1 / n2
        case '^': return n1 ** n2
        case 'sin': return math.sin(n1)
        case 'cos': return math.cos(n1)
        case 'tan': return math.tan(n1)
        case 'ln': return math.log(n1)
        case 'log': return math.log10(n1)
        case 'sqrt': return math.sqrt(n1)
        case 'abs': return abs(n1)
        case _: raise ValueError(f'Invalid operator received: {operator}')

def is_operator(char):
    operators = ['+', '-', '*', '/', '(', ')', '^']
    return char in operators

def is_func(name):
    valid_funcs = ['sin', 'cos', 'tan', 'ln', 'log', 'sqrt', 'abs']
    return name in valid_funcs

PARSE_END = '_'
def parse_equation(eq):
    eq = '(' + eq + ')'
    eq += ' ' + PARSE_END

    parsed_equation = []
    is_digit = False
    num = ''
    func_name = ''

    for i in range(len(eq)):
        if eq[i] == ' ':
            continue
        if eq[i] == PARSE_END:
            break

        #parse numbers
        is_digit = lambda x: x.isdigit() or (x == '.' and not '.' in num)
        if is_digit(eq[i]):
            num += eq[i]
            if not eq[i+1].isdigit() and not eq[i+1] == '.':
                parsed_equation.append(float(num))
                num = ''

        #parse operators
        if is_operator(eq[i]):
            parsed_equation.append(eq[i])

        #parse function names
        if not is_operator(eq[i]) and not is_digit(eq[i]) and not eq[i] == '.':
            func_name += eq[i]
            if is_digit(eq[i+1]) or is_operator(eq[i+1]):
                if is_func(func_name):
                    parsed_equation.append(func_name)

                elif func_name == 'pi':
                    parsed_equation.append(math.pi)
                elif func_name == 'e':
                    parsed_equation.append(math.e)
                else:
                    raise ValueError(f'Unrecognized function or character: {func_name}')
                func_name = ''

    #convert (x)(y) notation to (x)*(y)
    for i in range(len(parsed_equation) - 1):
        prev_item = parsed_equation[i]
        item = parsed_equation[i + 1]
        if prev_item == ')' and item == '(':
            parsed_equation.insert(i + 1, '*')

    #replace things like 10*-2 to 10 * -1 * 2
    queue = []
    for i in range(len(parsed_equation) - 1):
        prev_item = parsed_equation[i]
        item = parsed_equation[i + 1]
        if item == '-' and not(prev_item == ')' or type(prev_item) == type(0.0)):
            queue.append(i+1)
    offset = 0
    for i in queue:
        idx = i + offset
        parsed_equation.pop(idx)
        parsed_equation.insert(idx, '*')
        parsed_equation.insert(idx, -1.0)
        offset += 1

    return parsed_equation

main()