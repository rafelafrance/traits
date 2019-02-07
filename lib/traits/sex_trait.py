"""Parse sex notations."""

import re
from lib.trait import Trait
from lib.traits.base_trait import BaseTrait


class SexTrait(BaseTrait):
    """Parser logic."""

    def __init__(self, args=None):
        """Build the trait parser."""
        super().__init__(args)

        # Build the tokens
        self.kwd('keyword', 'sex')
        self.kwd('sex', r' females? | males? ')
        self.lit('quest', r' \? ')
        # These are words that indicate that "sex" is not a key
        self.kwd('skip', r' and | is | was ')
        self.lit('word', r' \b [a-z]\S* ')
        self.lit('sep', r' [;,"] | $ ')

        # Build a rules for parsing the trait
        self.product(
            self.convert,
            r""" keyword (?P<value> (?: sex | word ){1,2} (?: quest )? ) sep
                | keyword (?P<value> (?: sex | word ) (?: quest )? )
                | (?P<value> sex (?: quest )? )
                """)

        self.finish_init()

    def convert(self, token):
        """Convert parsed tokens into a result."""
        trait = Trait(
            value=token.groups['value'],
            start=token.start,
            end=token.end)
        trait.value = re.sub(r'\s*\?$', '?', trait.value, flags=self.flags)
        trait.value = re.sub(r'^m\w*', 'male', trait.value, flags=self.flags)
        trait.value = re.sub(r'^f\w*', 'female', trait.value, flags=self.flags)
        return trait
