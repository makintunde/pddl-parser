from unittest import TestCase
from ctl_star_goal import CtlStarGoal

PREFIX = 'CTL* '


class TestCtlStarGoal(TestCase):
    def test_get_evalutation_single(self):
        goal = [':goal']
        ctl_goal = CtlStarGoal(goal)
        expected_evaluation = PREFIX + 'goal'
        self.assertEqual(ctl_goal.get_evaluation(), expected_evaluation)

    def test_get_evaluation_double(self):
        goal = ['e', ['f', ['a', ['g', [':goal']]]]]
        ctl_goal = CtlStarGoal(goal)
        expected_evaluation = PREFIX + 'E ( F ( A ( G ( goal ) ) ) )'
        self.assertEqual(ctl_goal.get_evaluation(), expected_evaluation)

    def test_get_evaluation_triple(self):
        goal = ['implies', ['e', ['f', ['a']]], ['a', ['g', ['b']]]]
        ctl_goal = CtlStarGoal(goal)
        expeceted_evaluation = PREFIX + '( E ( F ( a ) ) ) -> ( A ( G ( b ) ) )'
        self.assertEqual(ctl_goal.get_evaluation(), expeceted_evaluation)

    def test_wrong_evaluation(self):
        goal = ['e', ['z'], ['a', ['b']], ['f', [':goal']]]
        ctl_goal = CtlStarGoal(goal)
        with self.assertRaises(Exception) as context:
            ctl_goal.get_evaluation()
        print context.exception
        expected_exception = 'Eval error: ' + str(goal) + ' is illegal'
        self.assertTrue(expected_exception in context.exception)
