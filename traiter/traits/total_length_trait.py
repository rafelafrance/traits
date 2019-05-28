"""Parse total length notations."""

import re
from functools import partial
from traiter.traits.numeric_trait import NumericTrait
import traiter.shared_tokens as tkn


LOOKBACK_FAR = 40
LOOKBACK_NEAR = 10
IS_ID = re.compile(
    r' id (?: ent )? (?: ifier )? | collector ',
    NumericTrait.flags)
IS_TRAP = re.compile(r' trap ', NumericTrait.flags)
IS_TESTES = re.compile(
    r' repoductive | gonad | test | scrot (?: al | um )? ',
    NumericTrait.flags)

LOOK_AROUND = 10
IS_LEFT = re.compile(r' \b r \b ', NumericTrait.flags)


class TotalLengthTrait(NumericTrait):
    """Parser logic."""

    def __init__(self, args=None):
        """Build the trait parser."""
        super().__init__(args)

        self._build_token_rules()
        self._build_product_rules()

        self.compile_regex()

    def _build_token_rules(self):
        self.shared_token(tkn.uuid)

        self.kwd('skip', r' horns? ')

        self.kwd('key_with_units', r"""
            (?: total | snout \s* vent | head \s* body | fork ) \s*
            len (?: gth )? \s* in \s* (?P<units> millimeters | mm )
            """)

        self.lit('key', r"""
            total  [\s-]* length [\s-]* in
            | (?: total | max | standard ) [\s-]* lengths? \b
            | meas [\s*:]? \s* length [\s(]* [l] [)\s:]*
            | meas (?: [a-z]* )? \.? : \s* l (?! [a-z.] )
            | t [o.]? \s? l \.? \s? _? (?! [a-z.] )
            | s \.? \s? l \.? (?! [a-z.] )
            | label [\s.]* lengths? \b
            | (?: fork | mean | body ) [\s-]* lengths? \b
            | s \.? \s? v \.? \s? l \.? (?! [a-z.] )
            | snout [\s-]* vent [\s-]* lengths? \b
            """)

        self.lit('ambiguous', r'(?<! [a-z] )(?<! [a-z] \s ) lengths? ')
        self.lit('key_units_req', r' measurements? | body | total ')
        self.shared_token(tkn.metric_len)
        self.shared_token(tkn.feet)
        self.shared_token(tkn.inches)
        self.shared_token(tkn.shorthand_key)
        self.shared_token(tkn.shorthand)
        self.shared_token(tkn.triple)
        self.shared_token(tkn.fraction)
        self.shared_token(tkn.pair)

        self.lit('char_key', r""" \b (?P<ambiguous_key> l ) (?= [:=-] ) """)

        self.kwd('word', r' (?: [a-z] \w* ) ')
        self.lit('semicolon', r' [;] | $ ')
        self.lit('comma', r' [,] | $ ')

    def _build_product_rules(self):
        self.product(self.fraction, r"""
            key_units_req fraction (?P<units> metric_len | feet | inches )
            | key fraction (?P<units> metric_len | feet | inches )
            | (?P<ambiguous_key> ambiguous) fraction
                (?P<units> metric_len | feet | inches )
            """)

        self.product(partial(self.compound, units=['ft', 'in']), r"""
            key (?P<ft> pair) feet (?: comma )? (?P<in> pair) inches
            | (?P<ambiguous_key>
                (?P<ft> pair) feet (?: comma )? (?P<in> pair) inches )
            """)

        self.product(self.simple, r"""
            key_with_units pair
            | shorthand_key (?: triple )? pair
                (?P<units> metric_len | feet | inches )
            | shorthand_key (?: triple )? (?P<units> metric_len ) pair
            | key_units_req (?: triple )? pair
                (?P<units> metric_len | feet | inches )
            | pair (?P<units> metric_len | feet | inches ) key
            | ambiguous (?: triple )? pair
                (?P<units> metric_len | feet | inches ) key
            | ambiguous (?: triple )?  pair key
            | (?P<ambiguous_key> ambiguous) pair
                (?P<units> metric_len | feet | inches )
            | (?P<ambiguous_key> ambiguous)
                (?P<units> metric_len | feet | inches ) pair
            | (?P<ambiguous_key> ambiguous) pair
            | key pair (?P<units> metric_len | feet | inches )
            | key (?P<units> metric_len | feet | inches ) pair
            | key (?: triple )? pair
            | key (?: word | semicolon | comma ){1,3} pair
                (?P<units> metric_len | feet | inches )
            | key (?: word | semicolon | comma ){1,3} pair
            | char_key pair (?P<units> metric_len | feet | inches )
            | char_key pair
            """)

        self.product(
            partial(self.shorthand_length, measurement='shorthand_tl'), r"""
            (?: shorthand_key | key_units_req ) shorthand | shorthand
            | (?: shorthand_key | key_units_req ) triple (?! shorthand | pair )
            """)

    def fix_up_trait(self, trait, text):
        """Fix problematic parses."""
        start = max(0, trait.start - LOOKBACK_FAR)
        if IS_ID.search(text, start, trait.start):
            return None
        start = max(0, trait.start - LOOKBACK_NEAR)
        if IS_TRAP.search(text, start, trait.start):
            return None

        if trait.ambiguous_key:
            start = max(0, trait.start - LOOK_AROUND)
            end = min(len(text), trait.end + LOOK_AROUND)
            if IS_TESTES.search(text, start, trait.start):
                return None
            if IS_LEFT.search(text, start, trait.start):
                return None
            if IS_LEFT.search(text, trait.end, end):
                return None

        return self.fix_up_inches(trait, text)