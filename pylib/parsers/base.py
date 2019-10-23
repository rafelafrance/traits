"""Common logic for parsing trait notations."""

from typing import List, Callable
import stacked_regex.stacked_regex as stacked
from stacked_regex.rule import Rule
from pylib.trait import Trait


def fix_up_nop(trait, text):  # pylint: disable=unused-argument
    """Fix problematic parses."""
    return trait


class Base(stacked.Parser):  # pylint: disable=too-few-public-methods
    """Shared lexer logic."""

    def __init__(
            self,
            scanners: List[Rule],
            replacers: List[Rule],
            producers: List[Rule],
            name: str = 'parser',
            fix_up: Callable[[Trait, str], Trait] = None) -> None:
        """Build the trait parser."""
        super().__init__(
            name=name,
            scanners=scanners,
            replacers=replacers,
            producers=producers)
        self.fix_up = fix_up if fix_up else fix_up_nop

    def parse(self, text, field=None):
        """Find the traits in the text.

        We get the trait list from the StackedRegex engine & then fix them up
        afterwards.
        """
        traits = []

        tokens = stacked.parse(text, self)

        for token in tokens:

            trait_list = token.action(token)

            # The action function can reject the token
            if not trait_list:
                continue

            # Some parses represent multiple traits, fix them all up
            if not isinstance(trait_list, list):
                trait_list = [trait_list]

            # Add the traits after any fix up.
            for trait in trait_list:
                trait = self.fix_up(trait, text)
                if trait:  # The parse may fail during fix up
                    if field:
                        trait.field = field
                    traits.append(trait)

        return traits


def convert(token):
    """Convert parsed tokens into a result."""
    return Trait(
        value=token.groups['value'].lower(),
        start=token.start, end=token.end)
