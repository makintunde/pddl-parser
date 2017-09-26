#!/usr/bin/env python

from code_generator import CodeGenerator
from pddl_parser import PddlParser
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Begin compilation.')
    parser.add_argument('directory', help='Name of directory containing the problem and domain files')
    parser.add_argument('domain', help='Name of PDDL file containing domain description')
    parser.add_argument('problem', help='Name of PDDL file containing problem')
    parser.add_argument('-d', action='store_true', help='Turn on debug mode')
   
    args = parser.parse_args()

    domain = args.domain + '.pddl'
    problem = args.problem + '.pddl'
    directory = args.directory
    parser = PddlParser(directory + domain, directory + problem)
    parser.parse()

    if args.d:
        parser.print_summary()
    else:
        code_generator = CodeGenerator(parser)
        code_generator.print_code()
