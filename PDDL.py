#!/usr/bin/env python
# Four spaces as indentation [no tabs]

from code_generator import CodeGenerator
from pddl_parser import PDDL_Parser
from action import Action

# ==========================================
# Main
# ==========================================
if __name__ == '__main__':
    import sys
    import pprint
    domain = sys.argv[1]
    problem = sys.argv[2]
    parser = PDDL_Parser(domain, problem)
    parser.parse()
    code_generator = CodeGenerator(parser)
    code_generator.print_code()
