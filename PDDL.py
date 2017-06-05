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
    domain_index = 2
    problem_index = 3

    if len(sys.argv) <= 3:
        # Shift arguments up by one for potential flags.
        domain_index -= 1
        problem_index -= 1
    else:
        flag = sys.argv[flag_index]

    domain = sys.argv[domain_index]
    problem = sys.argv[problem_index]
    parser = PddlParser(domain, problem)
    parser.parse()

    if flag == '-d':
        parser.print_summary()
    else:
        code_generator = CodeGenerator(parser)
        code_generator.print_code()
