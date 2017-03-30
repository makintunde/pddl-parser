#!/usr/bin/env python
# Four spaces as indentation [no tabs]

from code_generator import CodeGenerator
from pddl_parser import PddlParser

# ==========================================
# Main
# ==========================================
if __name__ == '__main__':
    import sys
    domain = sys.argv[1]
    problem = sys.argv[2]
    parser = PddlParser(domain, problem)
    parser.parse()
    parser.print_summary()
    code_generator = CodeGenerator(parser)
    #code_generator.print_code()
