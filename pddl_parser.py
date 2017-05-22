import re
import collections
from action import Action


class PddlParser:

    def __init__(self, domain, problem):
        self.domain = domain
        self.problem = problem
        self.actions = []
        self.predicates = []
        self.positive_goals = []
        self.negative_goals = []
        self.typed_objects = {}

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

    def parse_domain(self, domain_filename):
        tokens = self.scan_tokens(domain_filename)
        if type(tokens) is list and tokens.pop(0) == 'define':
            self.domain_name = 'unknown'

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

    def parse_predicates(self, group):
        while group:
            t = group.pop(0)
            if not type(t) is list:
                raise Exception(str(t) + 'is not recognized as a valid predicate.')
            without_dash = [c.replace('-','_') for c in t]
            self.predicates.append(without_dash)

    def get_predicates(self):
        return self.predicates

    def parse_problem(self, problem_filename):
        tokens = self.scan_tokens(problem_filename)
        if type(tokens) is list and tokens.pop(0) == 'define':
            self.problem_name = 'unknown'
            self.objects = []
            self.state = []
            self.typing = False

            while tokens:
                group = tokens.pop(0)
                t = group[0]
                if t == 'problem':
                    self.problem_name = group[-1]
                elif t == ':domain':
                    if self.domain_name != group[-1]:
                        raise Exception('Different domain specified in problem file')
                elif t == ':requirements':
                    group.pop(0)
                    self.requirements = group
                    self.typing = ':typing' in self.requirements
                elif t == ':objects':
                    if self.typing:
                        # Handle typing-specific parsing.
                        self.parse_typed_objects(group)
                    else:
                        group.pop(0)
                        self.objects = group
                elif t == ':init':
                    group.pop(0)
                    self.state = group
                elif t == ':goal':
                    self.split_propositions(group[1], self.positive_goals, self.negative_goals, '', 'goals')
                    self.positive_goals = self.remove_dashes(self.positive_goals)
                    self.negative_goals = self.remove_dashes(self.negative_goals)
                else:
                    print(str(t) + ' is not recognized in problem')

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
        self.scan_tokens(self.domain)
        self.scan_tokens(self.problem)
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
        self.parse_domain(self.domain)
        self.parse_problem(self.problem)

    def remove_dashes(self, goals):
        return [[item.replace('-', '_') for item in goal] for goal in goals]

    def parse_typed_objects(self, group):
        group.pop(0)
        while '-' in group:
            index_of_dash = group.index('-')
            objects = group[:index_of_dash]
            object_type = group[index_of_dash+1]
            self.typed_objects[object_type] = objects
            group = group[index_of_dash+2:]
