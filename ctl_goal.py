from extended_goal import ExtendedGoal


class CtlGoal(ExtendedGoal):
    def __init__(self, group):
        super(CtlGoal, self).__init__(group)

    def get_evaluation(self):
        return self.evaluation

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
                if op in ['eg', 'ef', 'ag', 'af']:
                    ans = op.upper() + ' ( ' + ans + ' )'
                elif op == 'not':
                    ans = '!( ' + ans + ' )'
                else:
                    ans = op + '_' + ans
                    self.atoms.append(ans)
            elif len(t) == 3:  # t is a list [and, t1, t2].
                ans1 = self.eval(t[1])
                ans2 = self.eval(t[2])
                ans = '( ' + ans1 + ' ) ' + t[0] + ' ( ' + ans2 + ' )'
            else:  # Something went wrong.
                print 'Eval error:', t, 'is illegal'
                raise Exception
        return ans