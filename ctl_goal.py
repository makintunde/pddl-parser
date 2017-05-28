from treenode import TreeNode


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

    def build_parse_tree(self, exp):
        fp_list = exp.split()
        p_stack = []  # A simple solution to keeping track of parents as we traverse the tree is to use a stack.
        e_tree = TreeNode()
        p_stack.append(e_tree)
        current_tree = e_tree
        for token in exp:
            if token == exp[0]:
                current_tree.left = TreeNode('')
                p_stack.append(current_tree)
                current_tree = current_tree.left
            elif token not in ['eg', 'ef', 'ag', 'af']:
                current_tree.val = token
                current_tree.right = TreeNode('')
                p_stack.append(current_tree)
                current_tree = current_tree.right
            elif token == exp[-1]:
                current_tree = p_stack.pop()
            else:
                raise ValueError
        return e_tree


