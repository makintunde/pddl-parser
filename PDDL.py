#!/usr/bin/env python
# Four spaces as indentation [no tabs]

from code_generator import CodeGenerator
from pddl_parser import PddlParser

# ==========================================
# Main
# ==========================================
if __name__ == '__main__':
    import sys

    flag = ''
    flag_index = 1
    problem_dir_index = 2
    domain_index = 3
    problem_index = 4

    if len(sys.argv) <= 4:
        # Shift arguments up by one for potential flags.
        problem_dir_index -= 1
        domain_index -= 1
        problem_index -= 1
    else:
        flag = sys.argv[flag_index]

    problem_dir = sys.argv[problem_dir_index]
    domain = sys.argv[domain_index] + '.pddl'
    problem = sys.argv[problem_index] + '.pddl'
    parser = PddlParser(problem_dir + domain, problem_dir + problem)
    parser.parse()

    if flag == '-d':
        parser.print_summary()
    else:
        code_generator = CodeGenerator(parser)
        code_generator.print_code()
