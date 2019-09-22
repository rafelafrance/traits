"""Parse testes state notations."""

from pylib.trait import Trait
from pylib.trait_builders.base_trait_builder import BaseTraitBuilder
from pylib.trait_builders.reproductive_trait_builder import MaleTraitBuilder
from pylib.shared_patterns import SharedPatterns
from pylib.shared_reproductive_patterns import ReproductivePatterns
import pylib.writers.csv_formatters.testes_state_csv_formatter as \
    testes_state_csv_formatter


class TestesStateTraitBuilder(BaseTraitBuilder, MaleTraitBuilder):
    """Parser logic."""

    csv_formatter = testes_state_csv_formatter.csv_formatter

    def build_token_rules(self):
        """Define the tokens."""
        tkn = SharedPatterns()
        r_tkn = ReproductivePatterns()

        # A label, like: "reproductive data"
        self.copy(r_tkn['label'])

        # Spellings of "testes"
        self.copy(r_tkn['testes'])

        # "Fully" or "incompletely"
        self.copy(r_tkn['fully'])

        # Negation: "non", "not", etc.
        self.copy(r_tkn['non'])

        # "Descended"
        self.copy(r_tkn['descended'])

        # Abbreviations for "testes"
        self.keyword('abbrev', 'tes ts tnd td tns ta t'.split())

        # Spellings of "scrotum"
        self.copy(r_tkn['scrotal'])

        # Spellings of "partially"
        self.copy(r_tkn['partially'])

        # Abbreviations for "testes state"
        self.keyword('state_abbrev', 'ns sc'.split())

        # Spellings of "abdominal"
        self.copy(r_tkn['abdominal'])

        # Various size words
        self.copy(r_tkn['size'])

        # Spellings of "gonads"
        self.copy(r_tkn['gonads'])

        # Other state words
        self.copy(r_tkn['other'])

        # We will skip over testes size measurements
        self.copy(tkn['cross'])
        self.copy(tkn['len_units'])

        self.copy(r_tkn['and'])

        # We allow random words in some situations
        self.copy(r_tkn['word'])

    def build_replace_rules(self):
        """Define rules for token simplification."""
        # Simplify state to contain various descended and size tokens
        self.replace('state', [
            'non fully descended',
            'abdominal non descended',
            'abdominal descended',
            'non descended',
            'fully descended',
            'partially descended',
            'size non descended',
            'size descended',
            'descended',
            'size'])

        # Simplify the testes length so it can be skipped easily
        self.replace('length', 'cross ( len_units )?')

    def build_product_rules(self):
        """Define rules for output."""
        # A typical testes state notation
        self.product(self.convert, [

            # E.g.: reproductiveData: ts 5x3 fully descended
            """label ( testes | abbrev )? ( length )?
                (?P<value> state | state_abbrev | abdominal | scrotal
                    | non scrotal | other | non testes )""",

            # E.g.: reproductive data = nonScrotal
            """label ( length )?
                (?P<value> non testes | non scrotal | scrotal )""",

            # E.g.: ts inguinal
            """abbrev ( length )?
                (?P<value> state | abdominal | non scrotal
                    | scrotal | other)""",

            # E.g.: testes 5x4 mm pt desc
            """testes ( length )?
                (?P<value>
                    ( state | state_abbrev | abdominal | non scrotal
                        | scrotal | other )
                    ( state | state_abbrev | abdominal | non scrotal
                        | scrotal | other | and ){,3}
                    ( state | state_abbrev | abdominal | non scrotal
                        | scrotal | other )
                )""",

            # E.g.: testes 5x4 desc
            """testes ( length )?
                (?P<value> state | state_abbrev | abdominal | non scrotal
                    | scrotal | other )""",

            # E.g.: no gonads
            """(?P<value> non ( testes | scrotal | gonads ) | scrotal )"""])

    @staticmethod
    def convert(token):
        """Convert parsed token into a trait product."""
        trait = Trait(
            value=token.groups['value'].lower(),
            start=token.start, end=token.end)
        trait.is_flag_in_token('ambiguous_key', token)
        return trait