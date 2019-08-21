"""Parse placental scar location notations."""

from lib.trait import Trait
from lib.trait_builders.base_trait_builder import BaseTraitBuilder
import lib.shared_repoduction_tokens as r_tkn


class PlacentalScarLocationTraitBuilder(BaseTraitBuilder):
    """Parser logic."""

    def __init__(self, args=None):
        """Build the trait parser."""
        super().__init__(args)

        self.build_token_rules()
        self.build_replace_rules()
        self.build_product_rules()

        self.compile_regex()

    def build_token_rules(self):
        """Define the tokens."""

        self.shared_token(r_tkn.word)

    def build_replace_rules(self):
        """Define rules for token simplification."""

    def build_product_rules(self):
        """Define rules for output."""
        self.product(self.convert, [
        ])

    @staticmethod
    def convert(token):
        """Convert parsed tokens into a result."""
        trait = Trait(
            value=token.groups['value'].lower(),
            start=token.start,
            end=token.end)
        return trait

    @staticmethod
    def should_skip(data, trait):
        """Check if this record should be skipped because of other fields."""
        if not data['sex'] or data['sex'][0].value != 'male':
            return False
        if data[trait]:
            data[trait].skipped = "Skipped because sex is 'male'"
        return True
