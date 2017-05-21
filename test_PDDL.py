#!/usr/bin/env python
# Four spaces as indentation [no tabs]

import unittest
from action import Action
from PDDL import PddlParser

# ==========================================
# Test PDDL
# ==========================================

class Test_PDDL(unittest.TestCase):

    # ------------------------------------------
    # Test scan_tokens
    # ------------------------------------------

    def test_scan_tokens_domain(self):
        parser = PddlParser()
        self.assertEqual(parser.scan_tokens('dinner/domain.pddl'),
            ['define', ['domain', 'dinner'],
            [':requirements', ':strips'],
            [':predicates', ['clean'], ['dinner'], ['quiet'], ['present'], ['garbage']],
            [':action', 'cook',
                ':parameters', [],
                ':precondition', ['and', ['clean']],
                ':effect', ['and', ['dinner']]],
            [':action', 'wrap',
                ':parameters', [],
                ':precondition', ['and', ['quiet']],
                ':effect', ['and', ['present']]],
            [':action', 'carry',
                ':parameters', [],
                ':precondition', ['and', ['garbage']],
                ':effect', ['and', ['not', ['garbage']], ['not', ['clean']]]],
            [':action', 'dolly',
                ':parameters', [],
                ':precondition', ['and', ['garbage']],
                ':effect', ['and', ['not', ['garbage']], ['not', ['quiet']]]]]
        )

    def test_scan_tokens_problem(self):
        parser = PddlParser()
        self.assertEqual(parser.scan_tokens('dinner/problem.pddl'),
            ['define', ['problem', 'pb1'],
            [':domain', 'dinner'],
            [':init', ['garbage'], ['clean'], ['quiet']],
            [':goal', ['and', ['dinner'], ['present'], ['not', ['garbage']]]]]
        )

    # ------------------------------------------
    # Test parse domain
    # ------------------------------------------

    def test_parse_domain(self):
        parser = PddlParser()
        parser.parse_domain('dinner/domain.pddl')
        self.assertEqual(parser.domain_name, 'dinner')
        self.assertEqual(parser.actions,
            [
                Action('cook', [], [['clean']], [], [['dinner']], []),
                Action('wrap', [], [['quiet']], [], [['present']], []),
                Action('carry', [], [['garbage']], [], [], [['garbage'], ['clean']]),
                Action('dolly', [], [['garbage']], [], [], [['garbage'], ['quiet']])
            ]
        )

    # ------------------------------------------
    # Test parse problem
    # ------------------------------------------

    def test_parse_problem(self):
        parser = PddlParser()
        parser.parse_domain('dinner/domain.pddl')
        parser.parse_problem('dinner/problem.pddl')
        self.assertEqual(parser.problem_name, 'pb1')
        self.assertEqual(parser.objects, [])
        self.assertEqual(parser.state, [['garbage'],['clean'],['quiet']])
        self.assertEqual(parser.positive_goals, [['dinner'], ['present']])
        self.assertEqual(parser.negative_goals, [['garbage']])

    #-------------------------------------------
    # Split propositions
    #-------------------------------------------

if __name__ == '__main__':
    unittest.main()