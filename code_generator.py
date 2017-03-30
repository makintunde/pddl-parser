import itertools


class CodeGenerator:
    
    def __init__(self, parser):
        self.parser = parser
        self.code_generator = []
        self.indentation_depth = 4
        self.agent_name = 'action'
        self.variable_map = {}
        self.effects = {}
        self.combinations = {}

    def add_line(self, depth, line):
        tabs = ' ' * (depth * self.indentation_depth)
        self.code_generator.append(tabs + line)

    def add_agent(self):
        self.add_line(0, 'Agent ' + self.agent_name)
        self.add_vars()
        self.add_redstates()
        self.prepare_actions()
        self.add_actions()
        self.add_protocol()
        self.add_evolution()
        self.add_line(0, 'end Agent')

    def initialise_variable_map(self):
        for s in self.parser.state:
            variable = '_'.join(s).replace('-', '')
            self.variable_map[variable] = True

    def add_vars(self):
        self.add_line(1, 'Vars:')
        var_type = 'boolean'
        predicates = self.parser.predicates
        objects = self.parser.objects
        for p in predicates:
            num_arguments = len(p) - 1
            combinations = list(itertools.permutations(objects, num_arguments))
            joined = [p[0] + '_' + '_'.join(comb) for comb in combinations]
            for j in joined:
                if j not in self.variable_map.keys():
                    self.variable_map[j.replace('-', '')] = False
                self.add_line(2, j + ' : ' + var_type + ';')
            
        self.add_line(1, 'end Vars')
    
    def add_redstates(self):
        self.add_line(1, 'RedStates:')
        self.add_line(1, 'end RedStates')

    def prepare_actions(self):
        for action in self.parser.actions:
            combinations = itertools.permutations(self.parser.objects, len(action.parameters))
            # TODO: negative_preconditions
            param_map = {action: i for i, action in enumerate(action.parameters)}
           
            for i, comb in enumerate(combinations):
                candidates = []
                negatives = []
                positives = []
                for precondition in action.positive_preconditions:
                    candidate = self.get_candidate(comb, param_map, precondition)
                    candidates.append(candidate)

                for positive in action.add_effects:
                    candidate = self.get_candidate(comb, param_map, positive)
                    positives.append(candidate + '=true')

                for negative in action.del_effects:
                    candidate = self.get_candidate(comb, param_map, negative)
                    negatives.append(candidate + '=false')

                next_combination = ' and '.join(candidate + '=true' for candidate in candidates)
                next_effect = ' and '.join(positives + negatives)
                
                action_name = action.name + str(i)

                # To be used for Evolution.
                self.effects[action_name] = next_effect
                self.combinations[action_name] = next_combination

    @staticmethod
    def get_candidate(comb, param_map, precondition):
        predicate = precondition[0].replace('-', '')
        arguments = [comb[param_map[p]] for p in precondition[1:]]
        candidate = '_'.join([predicate] + arguments)
        return candidate

    def add_actions(self):
        self.add_line(1, 'Actions = {')
        self.add_line(2, ', '.join(action for action, _ in self.effects.items()))
        self.add_line(1, '};')

    def add_protocol(self):
        self.add_line(1, 'Protocol:')
        for action_name, next_combination in self.combinations.items():
            next_str = next_combination + ' : { ' + action_name + ' };'
            self.add_line(2, next_str)
        self.add_line(1, 'end Protocol')

    def add_evolution(self):
        self.add_line(1, 'Evolution:')
        for action, effect in self.effects.items():
            next_line = effect + ' if Action=' + action + ';'
            self.add_line(2, next_line)
        self.add_line(1, 'end Evolution')

    def add_evaluation(self):
        self.add_line(0, 'Evaluation')

        goals = []
        positive_goals = ['action.' + '_'.join(goal) + '=true' for goal in self.parser.positive_goals]
        positive_goal_spec = ' and '.join(positive_goals)
        
        negative_goals = ['action.' + '_'.join(goal) + '=false' for goal in self.parser.negative_goals]
        negative_goal_spec = 'not ( ' + ' and '.join(negative_goals) + ' )'
        
        if positive_goals:
            goals.append(positive_goal_spec)
        if negative_goals:
            goals.append(negative_goal_spec)

        goal_spec = ' and '.join(goals)

        self.add_line(1, 'goal if ' + goal_spec + ';')
        self.add_line(0, 'end Evaluation')

    def add_init_states(self):
        self.add_line(0, 'InitStates')
        init_states = []
        for variable in self.variable_map:
            truth_strings = ['false', 'true']
            truth = truth_strings[self.variable_map[variable]]
            init_states.append(self.agent_name + '.' + variable + '=' + truth)
        self.add_line(1, ' and\n    '.join(init_states) + ';')
        self.add_line(0, 'end InitStates')

    def add_groups(self):
        self.add_line(0, 'Groups')
        self.add_line(1, 'g1 = { ' + self.agent_name + ' };')
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
