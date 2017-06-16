class ExtendedGoal(object):
    def __init__(self, group):
        self.atoms = []
        self.goal = group

    def __str__(self):
        return str(self.goal)

    def get_atoms(self):
        return self.atoms

    def get_evaluation(self):
        pass

    def eval(self, t):
        pass
