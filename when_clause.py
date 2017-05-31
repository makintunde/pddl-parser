class WhenClause(object):
    def __init__(self, precondition, postcondition):
        self.precondition = precondition
        self.positive_effects = []
        self.negative_effects = []
        self.get_effects(postcondition, self.positive_effects, self.negative_effects)

    def __str__(self):
        return '\nWhen clause: \n' + \
               'Precondition: ' + str(self.precondition) + ' \n' + \
               'Positive effects: ' + str(self.positive_effects) + ' \n' + \
               'Negative effects: ' + str(self.negative_effects) + ' \n'

    @staticmethod
    def get_effects(postcondition, positive_effects, negative_effects):
        if postcondition[0] == 'and':
            postcondition = postcondition[1:]
        if postcondition[0] == 'not':
            negative_effects.append(postcondition[-1])
        else:
            positive_effects.append(postcondition[0])
