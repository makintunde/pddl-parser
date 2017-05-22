import re
from predicate import Predicate
from action import Action


class PddlParser:

    def __init__(self, domain, problem):
        self.typed_predicates = []
        self.typing = False
        self.types = set()
        self.domain = domain
        self.problem = problem
        self.actions = []
        self.predicates = []
        self.positive_goals = []
        self.negative_goals = []
        self.typed_objects = {}

    def scan_tokens(self, filename):
        with open(filename, 'r') as f:
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
            self.typing = False

            while tokens:
                group = tokens.pop(0)
                t = group.pop(0)
                if t == 'domain':
                    self.domain_name = group[0]
                elif t == ':requirements':
                    self.typing = ':typing' in group
                elif t == ':predicates':
                    self.parse_predicates(group)
                elif t == ':types':
                    self.types = set(group)
                elif t == ':constants':
                    self.parse_typed_objects(group)
                elif t == ':action':
                    self.parse_action(group)
                else:
                    print(str(t) + ' is not recognized in domain')
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
        types = {}
        while group:
            t = group.pop(0)
            if t == ':parameters':
                if not type(group) is list:
                    raise Exception('Error with ' + name + ' parameters')
                parameters = self.parse_parameters(group.pop(0), types)
            elif t == ':precondition':
                self.split_propositions(group.pop(0), positive_preconditions, negative_preconditions, name, ' preconditions')
            elif t == ':effect':
                self.split_propositions(group.pop(0), add_effects, del_effects, name, ' effects')
            else:
                print(str(t) + ' is not recognized in action')
        action = Action(name, parameters, positive_preconditions, negative_preconditions, add_effects, del_effects, types)
        self.actions.append(action)

    def parse_predicates(self, group):
        if self.typing:
            self.parse_typed_predicates(group)
        else:
            while group:
                t = group.pop(0)
                if not type(t) is list:
                    raise Exception(str(t) + 'is not recognized as a valid predicate.')
                without_dash = map(self.remove_dashes_inner, t)
                self.predicates.append(without_dash)

    def remove_dashes_inner(self, item):
        return item.replace('-', '_')

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
                        group.pop(0)
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
            raise Exception('Error with ' + name + part)
        if group[0] == 'and':
            group.pop(0)
        else:
            group = [group]
        for proposition in group:
            if proposition[0] == 'not':
                if len(proposition) != 2:
                    raise Exception('Error with ' + name + ' negative' + part)
                neg.append(map(self.remove_dashes_inner, proposition[-1]))
            else:
                pos.append(map(self.remove_dashes_inner, proposition))

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
        return [map(self.remove_dashes_inner, goal) for goal in goals]

    def parse_typed_objects(self, group):
        while '-' in group:
            index_of_dash = group.index('-')
            objects = group[:index_of_dash]
            object_type = group[index_of_dash+1]
            if object_type in self.types:
                self.typed_objects[object_type] = objects
            else:
                raise Exception('Type "' + str(object_type) + '" is not recognised in domain.')
            group = group[index_of_dash+2:]

    def parse_typed_predicates(self, group):
        while group:
            to_parse = group.pop(0)
            predicate_name = to_parse.pop(0).replace('-', '_')
            type_of = {}

            while '-' in to_parse:
                index_of_dash = to_parse.index('-')
                arg = to_parse[index_of_dash-1]
                arg_type = to_parse[index_of_dash+1]
                if arg_type not in self.types:
                    raise Exception('Unknown type: "' + arg_type)
                type_of[arg] = arg_type
                to_parse = to_parse[index_of_dash+2:]

            self.typed_predicates.append(Predicate(predicate_name, type_of))

    def parse_parameters(self, param, types):
        while '-' in param:
            index_of_dash = param.index('-')
            param_type = param[index_of_dash+1]
            params = param[:index_of_dash]
            for p in params:
                types[p] = param_type
            param = param[index_of_dash+2:]

        if not types:
            return param

        return types.keys()
