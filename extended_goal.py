class ExtendedGoal(object):
    def __init__(self, group, goal_type=None):
        self.atoms = []
        self.goal = group
        self.goal_type = None
        if goal_type is not None:
            self.goal_type = goal_type

    def __str__(self):
        return str(self.get_evaluation())

    def get_atoms(self):
        return self.atoms

    def get_evaluation(self):
        pass

    def eval(self, t):
        pass
