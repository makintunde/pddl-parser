#!/usr/bin/env python
# Four spaces as indentation [no tabs]


class Action:

    def __init__(self, name, parameters, positive_preconditions, negative_preconditions, add_effects, del_effects,
                 types, agents=None, cost=0, plan_as_single_agent=True):
        self.agents = agents
        self.name = name
        self.parameters = parameters
        self.positive_preconditions = positive_preconditions
        self.negative_preconditions = negative_preconditions
        self.add_effects = add_effects
        self.del_effects = del_effects
        self.cost = cost
        self.types = types
        if plan_as_single_agent and self.agents:
            self.parameters += self.agents

    def __str__(self):
        result = 'action: ' + self.name + \
                 '\n  parameters: ' + str(self.parameters) + \
                 '\n  positive_preconditions: ' + str(self.positive_preconditions) + \
                 '\n  negative_preconditions: ' + str(self.negative_preconditions) + \
                 '\n  add_effects: ' + str(self.add_effects) + \
                 '\n  del_effects: ' + str(self.del_effects) + \
                 '\n  types: ' + str(self.types) + \
                 '\n  cost: ' + str(self.cost)
        if self.agents:
            result += '\n  agents: ' + str(list(self.agents))
        result += '\n'
        return result

    def __eq__(self, other): 
        return self.__dict__ == other.__dict__
