import collections
import itertools


class CodeGenerator:
    
    def __init__(self, parser):
        self.parser = parser
        self.code_generator = []
        self.indentation_depth = 4
        self.action_performing_agents = ['Performer']
        self.environment = 'Environment'
        self.variable_map = {}
        self.effects = {}
        self.combinations = {}
        self.goal_type = None

    def add_line(self, depth, line):
        tabs = ' ' * (depth * self.indentation_depth)
        self.code_generator.append(tabs + line)

    def add_environment_agent(self):
        self.add_line(0, 'Agent ' + self.environment)
        self.add_vars(obs=True)
        self.add_red_states()
        self.add_actions(empty=True)
        self.add_protocol(empty=True)
        self.add_evolution(self.action_performing_agents)
        self.add_line(0, 'end Agent')

    def add_action_performing_agent(self, agent_name):
        self.add_line(0, 'Agent ' + agent_name)
        self.add_vars(empty=True)
        self.prepare_actions()
        self.add_actions()
        self.add_protocol()
        self.add_evolution(agent_name, empty=True)
        self.add_line(0, 'end Agent')

    def initialise_variable_map(self):
        for s in self.parser.initial_state:
            variable = '_'.join(s)
            self.variable_map[variable] = True

    def add_vars(self, obs=None, empty=None):
        self.add_line(1, ('Vars' if obs is None else 'Obsvars') + ':')

        # Check whether we should generate an empty list of variables.
        if empty is not None:
            self.add_line(2, 'state : { empty };')
            self.add_line(1, 'end ' + ('Vars' if obs is None else 'Obsvars'))
            return

        if self.parser.typing:
            # Deal with typed objects and predicates.
            self.add_typed_vars()
        else:
            self.add_untyped_vars()

        self.add_line(1, 'end ' + ('Vars' if obs is None else 'Obsvars'))

    def add_untyped_vars(self):
        for p in self.parser.predicates:
            num_arguments = len(p) - 1
            combinations = list(itertools.permutations(self.parser.objects, num_arguments))
            joined = [p[0] + '_' + '_'.join(comb) for comb in combinations]
            for j in joined:
                if j[-1] == '_':  # trim
                    j = j[:-1]
                if j not in self.variable_map.keys():
                    self.variable_map[j] = False
                self.add_line(2, j + ' : boolean;')

    def add_red_states(self):
        self.add_line(1, 'RedStates:')
        self.add_line(1, 'end RedStates')

    def prepare_actions(self):
        for action in self.parser.actions:
            if self.parser.typing:
                self.prepare_typed_action(action)
            else:
                self.prepare_untyped_action(action)

    def prepare_typed_action(self, action):
        items = []
        for param in action.parameters:
            items.append([o for o, obj_type in self.parser.typed_objects.items() if action.types[param] == obj_type])
        combinations = itertools.product(*items)
        param_map = {action: i for i, action in enumerate(action.parameters)}
        self.get_preconditions_and_effects(action, combinations, param_map)

    def get_preconditions_and_effects(self, action, combinations, param_map):
        for i, comb in enumerate(combinations):
            candidates = set()
            negatives = set()
            positives = set()

            self.get_all_candidates(action, candidates, comb, negatives, param_map, positives)

            if negatives == positives:
                continue

            next_combination = ' and '.join(candidate + '=true' for candidate in candidates)
            with_effects = [p + '=true' for p in positives] + [n + '=false' for n in negatives]
            next_effect = ' and '.join(with_effects)

            action_name = '_'.join((action.name,) + comb)

            # To be used for Evolution.
            self.effects[action_name] = next_effect
            self.combinations[action_name] = next_combination

    def get_all_candidates(self, action, candidates, comb, negatives, param_map, positives):
        all_candidates = set()

        for precondition in action.positive_preconditions:
            candidate = self.get_candidate(comb, param_map, precondition)
            candidates.add('Environment.' + candidate)

        for positive in action.add_effects:
            candidate = self.get_candidate(comb, param_map, positive)
            if candidate in all_candidates:
                return
            positives.add(candidate)
            all_candidates.add(candidate)

        for negative in action.del_effects:
            candidate = self.get_candidate(comb, param_map, negative)
            if candidate in all_candidates:
                return
            negatives.add(candidate)
            all_candidates.add(candidate)

        return candidates, negatives, positives

    def prepare_untyped_action(self, action):
        combinations = itertools.permutations(self.parser.objects, len(action.parameters))
        param_map = {action: i for i, action in enumerate(action.parameters)}
        self.get_preconditions_and_effects(action, combinations, param_map)

    @staticmethod
    def get_candidate(comb, param_map, precondition):
        predicate = precondition[0]
        arguments = [comb[param_map[p]] for p in precondition[1:]]
        candidate = '_'.join([predicate] + arguments)
        return candidate

    def add_actions(self, empty=None):
        self.add_line(1, 'Actions = {')
        next_line = ', '.join(self.effects.keys())
        self.add_line(2, next_line if empty is None else 'none')
        self.add_line(1, '};')

    def add_protocol(self, empty=None):
        self.add_line(1, 'Protocol:')
        actions_without_precondition = set()

        if empty is not None:
            self.add_line(2, 'Other : { none };')
            self.add_line(1, 'end Protocol')
            return

        next_actions = collections.defaultdict(set)

        for action_name, next_combination in self.combinations.items():
            next_action = action_name
            if next_combination:
                next_actions[next_combination].add(next_action)
            else:
                actions_without_precondition.add(next_action)

        for precondition, actions in next_actions.items():
            enabled_actions = ' : { ' + ', '.join(actions.union(actions_without_precondition)) + ' };'
            self.add_line(2, precondition + enabled_actions)

        self.add_line(1, 'end Protocol')

    def add_evolution(self, agents, empty=None):
        self.add_line(1, 'Evolution:')
        if empty is None:
            for action, effect in self.effects.items():
                # Add effects for action-performing agent.
                for agent in agents:
                    next_line = effect + ' if ' + agent + '.Action=' + action + ';'
                    self.add_line(2, next_line)
        else:
            # Empty evolution.
            self.add_line(2, 'state=empty if state=empty;')
        self.add_line(1, 'end Evolution')

    def add_evaluation(self, agent_name):
        self.add_line(0, 'Evaluation')

        positive_goals = [agent_name + '.' + '_'.join(goal) + '=true' for goal in self.parser.positive_goals]
        positive_goal_spec = ' and '.join(positive_goals)

        negative_goals = [agent_name + '.' + '_'.join(goal) + '=false' for goal in self.parser.negative_goals]
        negative_goal_spec = ' and '.join(negative_goals)

        goals = []
        if positive_goals:
            goals.append(positive_goal_spec)
        if negative_goals:
            goals.append(negative_goal_spec)

        goal_spec = ' and '.join(goals)

        self.add_line(1, 'goal if ' + goal_spec + ';')

        if self.parser.goal_type in ['CTL', 'CTLSTAR']:
            for atom in self.parser.extended_goal.get_atoms():
                child = agent_name + '.' + atom + '=true'
                self.add_line(1, atom + ' if ' + child + ';')

        self.add_line(0, 'end Evaluation')

    def add_init_states(self, agent_name):
        self.add_line(0, 'InitStates')
        init_states = []
        for variable in self.variable_map:
            truth_strings = ['false', 'true']
            truth = truth_strings[self.variable_map[variable]]
            init_states.append(agent_name + '.' + variable + '=' + truth)
        self.add_line(1, ' and\n    '.join(init_states) + ';')
        self.add_line(0, 'end InitStates')

    def add_groups(self, agents):
        self.add_line(0, 'Groups')
        self.add_line(1, 'g1 = { ' + ', '.join(agents) + ' };')
        self.add_line(0, 'end Groups')

    def add_fairness(self):
        self.add_line(0, 'Fairness')
        self.add_line(0, 'end Fairness')

    def add_formulae(self):
        # TODO: Temporally-extended goals.
        self.add_line(0, 'Formulae')
        if self.parser.goal_type in ['CTL', 'CTLSTAR']:
            self.add_line(1, self.parser.extended_goal.get_evaluation() + ';')
        else:
            self.add_line(1, '<g1>F goal;')
        self.add_line(0, 'end Formulae')

    def generate(self):
        self.initialise_variable_map()
        self.prepare_actions()
        self.add_environment_agent()

        for agent in self.action_performing_agents:
            self.add_action_performing_agent(agent)

        self.add_evaluation(self.environment)
        self.add_init_states(self.environment)
        self.add_groups(self.action_performing_agents)
        self.add_fairness()
        self.add_formulae()
    
    def print_code(self):
        self.generate()
        for line in self.code_generator:
            print(line)

    def add_typed_vars(self):
        typed_predicates = self.parser.typed_predicates

        for t in typed_predicates:
            items = []
            name = t.get_name()
            args = t.get_arguments()
            for k, arg_type in args.items():
                items.append([o for o, obj_type in self.parser.typed_objects.items() if arg_type == obj_type])
            combinations = itertools.product(*items)
            for c in combinations:
                next_name = '_'.join((name,) + c)
                self.add_line(2, next_name + ' : boolean;')
                if next_name not in self.variable_map:
                    self.variable_map[next_name] = False
