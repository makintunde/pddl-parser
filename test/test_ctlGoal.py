from unittest import TestCase
from ctl_goal import CtlGoal


class TestCtlGoal(TestCase):
    def test_get_evalutation_single(self):
        goal = [':goal']
        ctl_goal = CtlGoal(goal)
        expected_evaluation = 'goal'
        self.assertEqual(ctl_goal.get_evaluation(), expected_evaluation)

    def test_get_evaluation_double(self):
        goal = ['ef', ['ag', [':goal']]]
        ctl_goal = CtlGoal(goal)
        expected_evaluation = 'EF ( AG ( goal ) )'
        self.assertEqual(ctl_goal.get_evaluation(), expected_evaluation)

    def test_get_evaluation_triple(self):
        goal = ['implies', ['ef', ['a']], ['ag', ['b']]]
        ctl_goal = CtlGoal(goal)
        expected_evaluation = '( EF ( a ) ) -> ( AG ( b ) )'
        self.assertEqual(ctl_goal.get_evaluation(), expected_evaluation)

    def test_wrong_evaluation(self):
        goal = ['e', ['z'], ['a', ['b']], ['f', [':goal']]]
        ctl_goal = CtlGoal(goal)
        with self.assertRaises(Exception) as context:
            ctl_goal.get_evaluation()
        expected_exception = 'Eval error: ' + str(goal) + ' is illegal'
        self.assertTrue(expected_exception in context.exception)

    def test_get_atoms(self):
        goal = ['until', ['and', ['free', 'left'], ['free', 'right']], [':goal']]
        ctl_goal = CtlGoal(goal)
        expected_atoms = ['free_left', 'free_right']
        self.assertEqual(ctl_goal.get_atoms(), expected_atoms)
