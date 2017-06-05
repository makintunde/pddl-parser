#!/usr/bin/env python
# Four spaces as indentation [no tabs]


class Action:

    def __init__(self, name, parameters, positive_preconditions, negative_preconditions, add_effects, del_effects,
                 positive_preconditions_or, negative_preconditions_or, add_effects_or, del_effects_or, types, cost=0):
        self.name = name
        self.parameters = parameters
        self.positive_preconditions = positive_preconditions
        self.negative_preconditions = negative_preconditions
        self.add_effects = add_effects
        self.del_effects = del_effects
        self.positive_preconditions_or = positive_preconditions_or
        self.negative_preconditions_or = negative_preconditions_or
        self.add_effects_or = add_effects_or
        self.del_effects_or = del_effects_or
        self.cost = cost
        self.types = types

    def __str__(self):
        return 'action: ' + self.name + \
               '\n  parameters: ' + str(self.parameters) + \
               '\n  positive_preconditions: ' + str(self.positive_preconditions) + \
               '\n  negative_preconditions: ' + str(self.negative_preconditions) + \
               '\n  positive_preconditions_or: ' + str(self.positive_preconditions_or) + \
               '\n  negative_preconditions_or: ' + str(self.negative_preconditions_or) + \
               '\n  add_effects: ' + str(self.add_effects) + \
               '\n  del_effects: ' + str(self.del_effects) + \
               '\n  add_effects_or: ' + str(self.add_effects_or) + \
               '\n  del_effects_or: ' + str(self.del_effects_or) + \
               '\n  types: ' + str(self.types) + \
               '\n  cost: ' + str(self.cost) + '\n'

    def __eq__(self, other): 
        return self.__dict__ == other.__dict__
