#!/usr/bin/env python
# Four spaces as indentation [no tabs]

import re
import itertools
from action import Action

class PDDL_Parser:

    # ------------------------------------------
    # Tokens
    # ------------------------------------------

    def scan_tokens(self, filename):
        with open(filename,'r') as f:
            # Remove single line comments
            str = re.sub(r';.*$', '', f.read(), flags=re.MULTILINE).lower()
        # Tokenize
        stack = []
        list = []
        for t in re.findall(r'[()]|[^\s()]+', str):
            if t == '(':
                stack.append(list)
                list = []
            elif t == ')':
                if stack:
                    l = list
                    list = stack.pop()
                    list.append(l)
                else:
                    raise Exception('Missing open parentheses')
            else:
                list.append(t)
        if stack:
            raise Exception('Missing close parentheses')
        if len(list) != 1:
            raise Exception('Malformed expression')
        return list[0]

    #-----------------------------------------------
    # Parse domain
    #-----------------------------------------------

    def parse_domain(self, domain_filename):
        tokens = self.scan_tokens(domain_filename)
        if type(tokens) is list and tokens.pop(0) == 'define':
            self.domain_name = 'unknown'
            self.actions = []
            self.predicates = []
            while tokens:
                group = tokens.pop(0)
                t = group.pop(0)
                if   t == 'domain':
                    self.domain_name = group[0]
                elif t == ':requirements':
                    pass # TODO
                elif t == ':predicates':
                    self.parse_predicates(group)
                elif t == ':types':
                    pass # TODO
                elif t == ':action':
                    self.parse_action(group)
                else: print(str(t) + ' is not recognized in domain')
        else:
            raise 'File ' + domain_filename + ' does not match domain pattern'

    #-----------------------------------------------
    # Parse action
    #-----------------------------------------------

    def parse_action(self, group):
        name = group.pop(0)
        if not type(name) is str:
            raise Exception('Action without name definition')
        for act in self.actions:
            if act.name == name:
                raise Exception('Action ' + name + 'redefined')
        parameters = []
        positive_preconditions = []
        negative_preconditions = []
        add_effects = []
        del_effects = []
        while group:
            t = group.pop(0)
            if t == ':parameters':
                if not type(group) is list:
                    raise Exception('Error with '+ name + ' parameters')
                parameters = group.pop(0)
            elif t == ':precondition':
                self.split_propositions(group.pop(0), positive_preconditions, negative_preconditions, name, ' preconditions')
            elif t == ':effect':
                self.split_propositions(group.pop(0), add_effects, del_effects, name, ' effects')
            else: print(str(t) + ' is not recognized in action')
        self.actions.append(Action(name, parameters, positive_preconditions, negative_preconditions, add_effects, del_effects))

    #-----------------------------------------------
    # Parse predicates
    #-----------------------------------------------
    def parse_predicates(self, group):
        while group:
            t = group.pop(0)
            if not type(t) is list:
                raise Exception(str(t) + 'is not recognized as a valid predicate.')
            self.predicates.append(t)

    def get_predicates(self):
        return self.predicates
    #-----------------------------------------------
    # Parse problem
    #-----------------------------------------------

    def parse_problem(self, problem_filename):
        tokens = self.scan_tokens(problem_filename)
        if type(tokens) is list and tokens.pop(0) == 'define':
            self.problem_name = 'unknown'
            self.objects = []
            self.state = []
            self.positive_goals = []
            self.negative_goals = []
            while tokens:
                group = tokens.pop(0)
                t = group[0]
                if   t == 'problem':
                    self.problem_name = group[-1]
                elif t == ':domain':
                    if self.domain_name != group[-1]:
                        raise Exception('Different domain specified in problem file')
                elif t == ':requirements':
                    pass # TODO
                elif t == ':objects':
                    group.pop(0)
                    self.objects = group
                elif t == ':init':
                    group.pop(0)
                    self.state = group
                elif t == ':goal':
                    self.split_propositions(group[1], self.positive_goals, self.negative_goals, '', 'goals')
                else: print(str(t) + ' is not recognized in problem')

    
    #-----------------------------------------------
    # Split propositions
    #-----------------------------------------------

    def split_propositions(self, group, pos, neg, name, part):
        if not type(group) is list:
            raise Exception('Error with '+ name + part)
        if group[0] == 'and':
            group.pop(0)
        else:
            group = [group]
        for proposition in group:
            if proposition[0] == 'not':
                if len(proposition) != 2:
                    raise Exception('Error with ' + name + ' negative' + part)
                neg.append(proposition[-1])
            else:
                pos.append(proposition)

    def print_summary(self):
        self.scan_tokens(domain)
        self.can_tokens(problem)
        print('Domain name:' + self.domain_name)
        print('Predicates: ' + str(self.predicates))
        for act in self.actions:
            print(act)
        print('----------------------------')
        print('Problem name: ' + self.problem_name)
        print('Objects: ' + str(self.objects))
        print('State: ' + str(self.state))
        print('Positive goals: ' + str(self.positive_goals))
        print('Negative goals: ' + str(self.negative_goals))
        
    def parse(self):
        self.parse_domain(domain)
        self.parse_problem(problem)


class CodeGenerator:
    
    def __init__(self, parser):
        self.parser = parser
        self.code_generator = []
        self.indentation_depth = 4
        self.agent_name = 'action'
        self.variable_map = {}

    def add_line(self, depth, line):
        tabs = ' ' * (depth * self.indentation_depth)
        self.code_generator.append(tabs + line)

    def add_agent(self):
        self.add_line(0, 'Agent ' + self.agent_name)
        self.add_vars()
        self.add_actions()
        self.add_protocol()
        self.add_evolution()
        self.add_line(0, 'End Agent')


    def add_vars(self):
        self.add_line(1, 'Vars:')
        var_type = 'boolean'
        predicates = self.parser.predicates
        objects = self.parser.objects
        variables = []
        for p in predicates:
            num_arguments = len(p) - 1
            combinations = list(itertools.combinations(objects, num_arguments))
            joined = [p[0] + '_' + '_'.join(comb) for comb in combinations]
            for j in joined:
                self.variable_map[j] = False
                self.add_line(2, j + ' : ' + var_type + ';')
            
        self.add_line(1, 'end Vars')
    
    def add_actions(self):
        self.add_line(1, 'Actions = {')
        # self.add_line(2, ...) 
        self.add_line(1, '};')
        pass # TODO

    def add_protocol(self):
        pass # TODO

    def add_evolution(self):
        pass # TODO

    def add_evaluation(self):
        pass # TODO

    def add_init_states(self):
        self.add_line(0, 'InitStates')
        init_states = []
        for s in parser.state:
            variable = '_'.join(s)
            self.variable_map[variable] = True
        for variable in self.variable_map:
            truth_strings = ['false', 'true']
            truth = truth_strings[self.variable_map[variable]]
            init_states.append(self.agent_name + '.' + variable + '=' + truth)
        self.add_line(1,' and\n    '.join(init_states))
        self.add_line(0, 'end InitStates')
        pass # TODO

    def add_groups(self):
        pass # TODO

    def add_fairness(self):
        pass # TODO

    def add_formulae(self):
        pass # TODO

    def generate(self):
        self.add_agent()
        self.add_evaluation()
        self.add_init_states()
        self.add_groups()
        self.add_fairness()
        self.add_formulae()
    
    def print_code(self):
        self.generate()
        for line in self.code_generator:
            print(line)



# ==========================================
# Main
# ==========================================
if __name__ == '__main__':
    import sys
    import pprint
    domain = sys.argv[1]
    problem = sys.argv[2]
    parser = PDDL_Parser()
    parser.parse()
    code_generator = CodeGenerator(parser)
    code_generator.print_code()
