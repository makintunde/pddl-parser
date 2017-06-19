from unittest import TestCase

from predicate_parser import PredicateParser


class TestPredicateParser(TestCase):
    def test_parse_typed_predicates_no_agent(self):
        group = [['on', '?x', '-', 'block', '?y', '-', 'block'],
                 ['ontable', '?x', '-', 'block'],
                 ['clear', '?x', '-', 'block']]

        types = {'object', 'block'}
        predicate_parser = PredicateParser(True, types)

        while group:
            to_parse = group.pop(0)
            predicate_parser.parse(to_parse)

        actual_predicates = predicate_parser.get_predicates()
        expected_predicates = [['on', '?x', '?y'], ['ontable', '?x'], ['clear', '?x']]
        self.assertEqual(actual_predicates, expected_predicates)

    def test_parse_typed_predicates_with_agent(self):
        group = [['on', '?x', '-', 'block', '?y', '-', 'block'],
                 ['ontable', '?x', '-', 'block'],
                 ['clear', '?x', '-', 'block'],
                 [':private', '?agent', '-', 'agent',
                  ['holding', '?agent', '-', 'agent', '?x', '-', 'block'],
                  ['handempty', '?agent', '-', 'agent']]]

        types = {'object', 'block', 'agent'}
        predicate_parser = PredicateParser(True, types)

        while group:
            to_parse = group.pop(0)
            predicate_parser.parse(to_parse)

        actual_predicates_all = predicate_parser.get_predicates()
        expected_predicates_all = [['on', '?x', '?y'], ['ontable', '?x'], ['clear', '?x'], ['handempty', '?agent'],
                                   ['holding', '?agent', '?x']]
        self.assertEqual(expected_predicates_all, actual_predicates_all)

        actual_predicates_private = predicate_parser.get_private_predicates()
        expected_predicates_private = [['handempty', '?agent'], ['holding', '?agent', '?x']]
        self.assertItemsEqual(actual_predicates_private, expected_predicates_private)
