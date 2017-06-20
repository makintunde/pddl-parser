from predicate import Predicate
from utils import remove_dashes_inner, parse_group
from visibilities import Visibilities


class PredicateParser(object):

    def __init__(self, typing, existing_types):
        self.private_typed_predicates = []
        self.predicates = []
        self.typed_predicates = []
        self.private_predicates = []
        self.public_predicates = []
        self.typing = typing
        self.types = existing_types
        self.agents = []

    def __str__(self):
        return str(self.predicates)

    def parse(self, to_parse):
        if self.typing:
            if to_parse[0] == ':private':
                self.parse_private_predicates(to_parse)
            else:
                self.parse_typed_predicates(to_parse)
        else:
            self.parse_untyped_predicates(to_parse)

    def parse_private_predicates(self, to_parse):
        private_predicates_to_parse = []
        while isinstance(to_parse[-1], list):
            private_predicates_to_parse.append(to_parse.pop())
        for to_parse in private_predicates_to_parse:
            self.parse_typed_predicates(to_parse, visibility=Visibilities.PRIVATE)

    def parse_typed_predicates(self, group, visibility=None):
        """
        Parse the typed predicates in the planning domain. Multi-agent domains are guaranteed to be typed.
        :param visibility: The visibilty of the predicate; PUBLIC or PRIVATE.
        :param group: The predicate construct to be parsed. 
        :return: (Side effects): Updates the predicates list with the names of the typed predicates,
                 and populates the typed_predicates list with Predicate objects.
        """
        predicate_name = remove_dashes_inner(group.pop(0))
        types = {}
        args = []

        while '-' in group:
            group, objects = parse_group(group, types, self.types)
            args.extend(objects)

        self.predicates.append([predicate_name] + args)
        self.typed_predicates.append(Predicate(predicate_name, types))
        if visibility is not None and visibility == Visibilities.PRIVATE:
            self.private_predicates.append([predicate_name] + args)
            self.private_typed_predicates.append(Predicate(predicate_name, types))

    def parse_untyped_predicates(self, group):
        without_dash = map(remove_dashes_inner, group)
        self.predicates.append(without_dash)

    def get_predicates(self):
        return self.predicates

    def get_typed_predicates(self):
        return self.typed_predicates

    def get_private_predicates(self):
        return self.private_predicates

    def get_private_typed_predicates(self):
        return self.private_typed_predicates

    def get_public_predicates(self):
        return [p for p in self.predicates if p not in self.private_predicates]

    def get_public_typed_predicates(self):
        return [p for p in self.typed_predicates if p not in self.private_typed_predicates]
