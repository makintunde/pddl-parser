import re
from predicate import Predicate
from action import Action
from ctl_goal import CtlGoal
from ctl_star_goal import CtlStarGoal
from initial_state import InitState


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
        self.positive_goals_or = []
        self.negative_goals_or = []
        self.extended_goal = None
        self.negative_goals = []
        self.typed_objects = {}
        self.goal_type = None
        self.function = None

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
                elif t == ':predicates':
                    self.parse_predicates(group)
                elif t == ':types':
                    self.types = set(group)
                elif t == ':constants':
                    self.parse_typed_objects(group, self.typed_objects)
                elif t == ':functions':
                    self.functions = self.parse_functions(group)
                elif t == ':action':
                    self.parse_action(group)
                else:
                    print(str(t) + ' is not recognized in domain')
        else:
            raise 'File ' + domain_filename + ' does not match domain pattern'

    def parse_action(self, group):
        name = self.remove_dashes_inner(group.pop(0))
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
        positive_preconditions_or = []
        negative_preconditions_or = []
        add_effects_or = []
        del_effects_or = []
        types = {}
        while group:
            t = group.pop(0)
            if t == ':parameters':
                if not type(group) is list:
                    raise Exception('Error with ' + name + ' parameters')
                parameters = self.parse_typed_objects(group.pop(0), types)
            elif t == ':precondition':
                self.split_propositions(group.pop(0), positive_preconditions, negative_preconditions,
                                        positive_preconditions_or, negative_preconditions_or, name, ' preconditions')
            elif t == ':effect':
                self.split_propositions(group.pop(0), add_effects, del_effects, add_effects_or, del_effects_or, name,
                                        ' effects')
            else:
                print(str(t) + ' is not recognized in action')
        action = Action(name, parameters, positive_preconditions, negative_preconditions, add_effects, del_effects,
                        positive_preconditions_or, negative_preconditions_or, add_effects_or, del_effects_or, types)
        self.actions.append(action)

    def parse_typed_predicates(self, group):
        predicate_name = self.remove_dashes_inner(group.pop(0))
        types = {}
        args = []

        while '-' in group:
            group, objects = self.parse_group(group, types)
            args.extend(objects)

        self.predicates.append([predicate_name] + args)
        self.typed_predicates.append(Predicate(predicate_name, types))

    def parse_group(self, group, types):
        index_of_dash = group.index('-')
        obj_type = group[index_of_dash+1]
        if obj_type not in self.types:
            raise Exception('Type "' + str(obj_type) + '" is not recognised in domain.')
        objects = group[:index_of_dash]
        for obj in objects:
            types[obj] = obj_type
        group = group[index_of_dash+2:]
        return group, objects

    def parse_predicates(self, group):
        while group:
            to_parse = group.pop(0)
            if not type(to_parse) is list:
                raise Exception(str(to_parse) + 'is not recognized as a valid predicate.')
            if self.typing:
                self.parse_typed_predicates(to_parse)
            else:
                without_dash = map(self.remove_dashes_inner, to_parse)
                self.predicates.append(without_dash)

    @staticmethod
    def remove_dashes_inner(item):
        return item   # return item.replace('-', '_')

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
                    if self.typing:
                        # Handle typing-specific parsing.
                        group.pop(0)
                        self.objects = self.parse_typed_objects(group, self.typed_objects)
                    else:
                        group.pop(0)
                        self.objects = map(self.remove_dashes_inner, group)
                elif t == ':init':
                    group.pop(0)
                    self.initial_state = self.parse_initial_state(group)
                elif t == ':goal':
                    self.split_propositions(group[1], self.positive_goals, self.negative_goals, self.positive_goals_or,
                                            self.negative_goals_or, '', 'goals')
                    self.positive_goals = self.remove_dashes(self.positive_goals)
                    self.negative_goals = self.remove_dashes(self.negative_goals)
                elif t in [':ctlgoal', ':stronggoal']:
                    self.extended_goal = CtlGoal(group[1], goal_type=group[0])
                    self.goal_type = 'CTL'
                elif t == ':ctlstargoal':
                    self.extended_goal = CtlStarGoal(group[1])
                    self.goal_type = 'CTLSTAR'
                else:
                    raise Exception(str(t) + ' is not recognized in problem')

    def split_propositions(self, group, pos, neg, pos_ors, neg_ors, name, part):
        if not type(group) is list:
            raise Exception('Error with ' + name + part)
        using_and = False
        if group[0] in ['and', 'or']:
            using_and = group[0] == 'and'
            group.pop(0)
        else:
            group = [group]
        for proposition in group:
            if proposition[0] == 'not':
                if len(proposition) != 2:
                    raise Exception('Error with ' + name + ' negative' + part)
                if using_and:
                    neg.append(map(self.remove_dashes_inner, proposition[-1]))
                else:
                    neg_ors.append(map(self.remove_dashes_inner, proposition[-1]))
            else:
                if using_and:
                    pos.append(map(self.remove_dashes_inner, proposition))
                else:
                    pos_ors.append(map(self.remove_dashes_inner, proposition))

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

    def remove_dashes(self, goals):
        return [map(self.remove_dashes_inner, goal) for goal in goals]

    def parse_typed_objects(self, group, types):
        while '-' in group:
            group, objects = self.parse_group(group, types)

        if not types:
            return map(self.remove_dashes_inner, group)

        return types.keys()

    @staticmethod
    def parse_initial_state(group):
        return InitState(group)

    def parse_functions(self, group):
        types = {}
        index_of_dash = group.index('-')
        obj_type = group[index_of_dash + 1]
        if obj_type not in self.types:
            raise Exception('Type "' + str(obj_type) + '" is not recognised in domain.')
        (objects,) = group[:index_of_dash]
        for obj in objects:
            types[obj] = obj_type

        args = objects
        self.predicates.append(['='] + args)
        self.typed_predicates.append(Predicate('=', types))

        return objects
