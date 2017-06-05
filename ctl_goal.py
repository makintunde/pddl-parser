from extended_goal import ExtendedGoal


class CtlGoal(ExtendedGoal):
    def __init__(self, group, goal_type=None):
        if goal_type is not None:
            self.goal_type = goal_type
            super(CtlGoal, self).__init__(group, self.goal_type)
        else:
            super(CtlGoal, self).__init__(group)

    def get_evaluation(self):
        return self.eval(self.goal)

    def eval(self, t):
        """
        :param t: a TREE,
                  where TREE ::= ATOM | [AND, TREE, TREE] | [OP, TREE]
                        OP := EG | EF | AG | AF | NOT
                        ATOM := a list of strings
        :return: the infix string representing the tree t.
        """
        if isinstance(t, str):
            ans = t
        else:  # t is a list
            if len(t) == 1:  # t is a singleton [t].
                ans = t[0]
                if ans[0] == ':':
                    ans = ans[1:]
            elif len(t) == 2:  # t is a list [op, t].
                op = t[0]
                ans = self.eval(t[1])
                if op in ['eg', 'ef', 'ag', 'af', 'ax', 'ex']:
                    ans = op.upper() + ' ( ' + ans + ' )'
                elif op == 'not':
                    ans = '!( ' + ans + ' )'
                else:
                    ans = op + '_' + ans
                    self.atoms.append(ans)
            elif len(t) == 3:  # t is a list [and, t1, t2].
                ans1 = self.eval(t[1])
                ans2 = self.eval(t[2])
                op = t[0]

                if op == 'implies':
                    op = '->'
                elif op == 'until':
                    op = 'U'

                ans = '( ' + ans1 + ' ) ' + op + ' ( ' + ans2 + ' )'
                if op == 'U':
                    ans = 'E (' + ans + ')'
                elif self.goal_type is not None:
                    goal_map = {':stronggoal': 'AF', ':weakgoal': 'EF'}
                    ans = goal_map[self.goal_type] + ' ( ' + ans + ' ) '
            else:  # Something went wrong.
                print 'Eval error:', t, 'is illegal'
                raise Exception
        return ans
