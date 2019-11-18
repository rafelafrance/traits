"""A class to hold an individual token."""

from typing import Dict, List, Match, Tuple
from pylib.stacked_regex.rule import Rule, Action, Groups


Tokens = List['Token']


class Token:
    """A token is the result of a rule match."""

    def __init__(
            self,
            rule: Rule = None,
            match: Match = None,
            groups: Groups = None,
            span: Tuple[int, int] = None) -> None:
        """Create a token."""
        self.rule = rule
        self.match = match
        self.span = span if span else (0, 0)
        self.groups = groups if groups else {}

        if match:
            self.span = match.span()
            self.groups = {k: v for k, v in match.groupdict().items()
                           if v is not None}

    def __repr__(self) -> str:
        """Create string form of the object."""
        return '{}({})'.format(self.__class__.__name__, self.__dict__)

    def __eq__(self, other: 'Token') -> bool:
        """Compare tokens."""
        return self.__dict__ == other.__dict__

    @property
    def __dict__(self) -> Dict:
        """Convert to a string."""
        return {
            'name': self.name,
            'span': self.span,
            'groups': self.groups}

    @property
    def name(self) -> str:
        """Return the rule name."""
        return self.rule.name

    @property
    def start(self) -> int:
        """Return the match start."""
        return self.span[0]

    @property
    def end(self) -> int:
        """Return the match end."""
        return self.span[1]

    @property
    def action(self) -> Action:
        """Return the rule name."""
        return self.rule.action


def forget(token):
    """Forget all of the capture groups."""
    token.groups = {}