class ForAllEffect(object):
    def __init__(self, x, condition_formula):
        self.types = {x[0]: x[-1]}
        self.x = x[0]
        self.condition_formula = condition_formula

    def types(self):
        return self.types

    def __str__(self):
        return str([self.x] + self.condition_formula)

    def __repr__(self):
        return self.__str__()
