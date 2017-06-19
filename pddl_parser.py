import re

from action import Action
from ctl_goal import CtlGoal
from ctl_star_goal import CtlStarGoal
from initial_state import InitState
from predicate_parser import PredicateParser
from utils import remove_dashes_inner, remove_dashes, parse_group


class PddlParser:

    def __init__(self, domain, problem):
        self.typed_predicates = []
        self.typing = False
        self.types = set()
        self.domain = domain
        self.domain_name = None
        self.problem = problem
        self.problem_name = None
        self.actions = []
        self.predicates = []
        self.positive_goals = []
        self.extended_goal = None
        self.negative_goals = []
        self.typed_objects = {}
        self.goal_type = None
        self.agents = None
        self.multi_agent = None

    def scan_tokens(self, filename):
        # TODO: Replace 'tokens' with AST?
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
                    self.multi_agent = ':multi-agent' in group
                elif t == ':predicates':
                    self.parse_predicates(group)
                elif t == ':types':
                    self.types = set(group)
                elif t == ':constants':
                    self.parse_typed_objects(group, self.typed_objects)
                elif t == ':action':
                    self.parse_action(group)
                else:
                    print(str(t) + ' is not recognized in domain')
        else:
            raise 'File ' + domain_filename + ' does not match domain pattern'

    def parse_action(self, group):
        name = remove_dashes_inner(group.pop(0))
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
                parameters = self.parse_typed_objects(group.pop(0), types)
            elif t == ':precondition':
                self.split_propositions(group.pop(0), positive_preconditions, negative_preconditions, name, ' preconditions')
            elif t == ':effect':
                self.split_propositions(group.pop(0), add_effects, del_effects, name, ' effects')
            else:
                print(str(t) + ' is not recognized in action')
        action = Action(name, parameters, positive_preconditions, negative_preconditions, add_effects, del_effects, types)
        self.actions.append(action)

    def parse_predicates(self, group):
        predicate_parser = PredicateParser(self.typing, self.types)
        while group:
            to_parse = group.pop(0)
            if not type(to_parse) is list:
                raise Exception(str(to_parse) + 'is not recognized as a valid predicate.')
            predicate_parser.parse(to_parse)
        self.predicates = predicate_parser.get_predicates()
        self.typed_predicates = predicate_parser.get_typed_predicates()

    def get_predicates(self):
        return self.predicates

    def parse_problem(self, problem_filename):
        tokens = self.scan_tokens(problem_filename)
        if type(tokens) is list and tokens.pop(0) == 'define':
            self.problem_name = 'unknown'
            self.objects = []
            self.initial_state = []

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
                    self.parse_objects(group)
                elif t == ':init':
                    group.pop(0)
                    self.initial_state = self.parse_initial_state(group)
                elif t == ':goal':
                    self.split_propositions(group[1], self.positive_goals, self.negative_goals, '', 'goals')
                    self.positive_goals = remove_dashes(self.positive_goals)
                    self.negative_goals = remove_dashes(self.negative_goals)
                elif t == ':ctlgoal':
                    self.extended_goal = CtlGoal(group[1])
                    self.goal_type = 'CTL'
                elif t == ':ctlstargoal':
                    self.extended_goal = CtlStarGoal(group[1])
                    self.goal_type = 'CTLSTAR'
                else:
                    raise Exception(str(t) + ' is not recognized in problem')

    def parse_objects(self, group):
        group.pop(0)
        if self.typing:
            # Handle typing-specific parsing.
            self.objects, self.agents = self.parse_typed_objects(group, self.typed_objects)
        else:
            self.objects = map(remove_dashes_inner, group)

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
                neg.append(map(remove_dashes_inner, proposition[-1]))
            else:
                pos.append(map(remove_dashes_inner, proposition))

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
        print('Initial state: ' + str(self.initial_state))
        print('Positive goals: ' + str(self.positive_goals))
        print('Negative goals: ' + str(self.negative_goals))
        print('CTL goals: ' + str(self.extended_goal))
        
    def parse(self):
        self.parse_domain(self.domain)
        self.parse_problem(self.problem)

    def parse_typed_objects(self, group, types):
        while '-' in group:
            group, objects = parse_group(group, types, self.types)

        if not types:
            return map(remove_dashes_inner, group)

        agents = set()
        while group:
            next_group = group.pop(0)
            if next_group[0] == ':private' and next_group[-1] == 'agent':
                if '-' in next_group:
                    # Extract the name of the agent, which is the last string before the '-'.
                    agents.add(next_group[next_group.index('-')-1])
        return types.keys(), agents

    @staticmethod
    def parse_initial_state(group):
        return InitState(group)
