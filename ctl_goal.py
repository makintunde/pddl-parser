class CtlGoal(object):
    def __init__(self, group):
        self.goal = group

    def __str__(self):
        return str(self.goal)

    def parse_ctl_goal(self, goal):
        egs, efs, afs, ags = [], [], [], []
        if not type(goal) is list:
            raise Exception('Error with CTL goal ' + goal)
        if goal[0] == 'and':
            goal.pop(0)
        else:
            goal = [goal]
        for proposition in goal:
            if proposition[0] == 'eg':
                egs.append('_'.join(proposition[-1]))
            elif proposition[0] == 'ef':
                efs.append('_'.join(proposition[-1]))
            elif proposition[0] == 'af':
                afs.append('_'.join(proposition[-1]))
            elif proposition[0] == 'ag':
                ags.append('_'.join(proposition[-1]))
