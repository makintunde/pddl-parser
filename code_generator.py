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

        predicates = self.parser.predicates
        objects = self.parser.objects
        for p in predicates:
            num_arguments = len(p) - 1
            combinations = list(itertools.permutations(objects, num_arguments))
            joined = [p[0] + '_' + '_'.join(comb) for comb in combinations]
            for j in joined:
                if j[-1] == '_':  # trim
                    j = j[:-1]
                if j not in self.variable_map.keys():
                    self.variable_map[j.replace('-', '_')] = False
                self.add_line(2, j + ' : boolean;')

        self.add_line(1, 'end ' + ('Vars' if obs is None else 'Obsvars'))
    
    def add_red_states(self):
        self.add_line(1, 'RedStates:')
        self.add_line(1, 'end RedStates')

    def prepare_actions(self):
        for action in self.parser.actions:
            combinations = itertools.permutations(self.parser.objects, len(action.parameters))
            param_map = {action: i for i, action in enumerate(action.parameters)}
           
            for i, comb in enumerate(combinations):
                candidates = []
                negatives = []
                positives = []

                for precondition in action.positive_preconditions:
                    candidate = self.get_candidate(comb, param_map, precondition)
                    candidates.append('Environment.' + candidate)

                for positive in action.add_effects:
                    candidate = self.get_candidate(comb, param_map, positive)
                    positives.append(candidate + '=true')

                for negative in action.del_effects:
                    candidate = self.get_candidate(comb, param_map, negative)
                    negatives.append(candidate + '=false')

                next_combination = ' and '.join(candidate + '=true' for candidate in candidates)
                next_effect = ' and '.join(positives + negatives)
                
                action_name = '_'.join((action.name,) + comb)

                # To be used for Evolution.
                self.effects[action_name] = next_effect
                self.combinations[action_name] = next_combination

    @staticmethod
    def get_candidate(comb, param_map, precondition):
        predicate = precondition[0].replace('-', '_')
        arguments = [comb[param_map[p]] for p in precondition[1:]]
        candidate = '_'.join([predicate] + arguments)
        return candidate

    def add_actions(self, empty=None):
        self.add_line(1, 'Actions = {')
        next_line = ', '.join(action.replace('-', '_') for action in self.effects.keys())
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
            next_action = action_name.replace('-', '_')
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
                    next_line = effect + ' if ' + agent + '.Action=' + action.replace('-', '_') + ';'
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
        self.add_line(0, 'Formulae')
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
