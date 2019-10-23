"""Parse ovaries state notations."""

import re
from stacked_regex.rule import fragment, keyword, producer, replacer
from pylib.trait import Trait
from pylib.parsers.base import Base
from pylib.shared_patterns import SHARED
from pylib.shared_reproductive_patterns import REPRODUCTIVE


def convert(token):
    """Convert parsed token into a trait."""
    value = token.groups['value'].lower()
    if re.match(r'^[\s\d]+$', value):
        return None
    trait = Trait(
        value=value,
        start=token.start, end=token.end)
    trait.is_flag_in_token('ambiguous_key', token)
    trait.is_value_in_token('side', token)
    return trait


def double(token):
    """Convert a single token into two traits."""
    trait1 = Trait(
        value=token.groups['value_a'].lower(),
        side=token.groups['side_a'].lower(),
        start=token.start,
        end=token.end)

    trait2 = Trait(
        value=token.groups['value_b'].lower(),
        side=token.groups['side_b'].lower(),
        start=token.start,
        end=token.end)

    return [trait1, trait2]


OVARIES_STATE = Base(
    name=__name__.split('.')[-1],
    scanners=[
        REPRODUCTIVE['ovary'],
        REPRODUCTIVE['size'],
        REPRODUCTIVE['uterus'],
        REPRODUCTIVE['fallopian'],
        REPRODUCTIVE['mature'],
        REPRODUCTIVE['active'],
        REPRODUCTIVE['non'],
        REPRODUCTIVE['visible'],
        REPRODUCTIVE['destroyed'],
        REPRODUCTIVE['developed'],
        REPRODUCTIVE['count'],
        REPRODUCTIVE['horns'],
        REPRODUCTIVE['covered'],
        REPRODUCTIVE['fat'],
        REPRODUCTIVE['lut'],
        REPRODUCTIVE['corpus'],
        REPRODUCTIVE['alb'],
        REPRODUCTIVE['nipple'],
        SHARED['side'],
        SHARED['cyst'],
        REPRODUCTIVE['color'],
        REPRODUCTIVE['texture'],
        REPRODUCTIVE['sign'],
        REPRODUCTIVE['and'],
        SHARED['cross'],
        SHARED['len_units'],

        # Skip words
        keyword('skip', ' womb '),

        fragment('sep', r' [;] '),

        # We allow random words in some situations
        fragment('word', r'[a-z] \w*'),
    ],

    replacers=[
        # E.g.: ovaries and uterine horns
        # Or:   ovaries and fallopian tubes
        replacer('ovaries', r"""
            ovary ( ( ( and )? uterus ( horns )? )
                    | ( and )? fallopian )?
            """),

        # E.g.: covered in copious fat
        replacer('coverage', ' covered (word){0,2} fat '),

        # E.g.: +corpus luteum
        replacer('luteum', ' ( sign )? ( corpus )? (alb | lut) '),

        # E.g.: active
        # Or:   immature
        replacer('state', """
            (non)? ( active | mature | destroyed | visible | developed )"""),

        # Skip nipple notation
        replacer('nips', 'nipple ( size | state )'),

        # E.g.: 6 x 4 mm
        replacer('measurement', [
            'cross len_units',
            'len_units cross',
            'cross']),
    ],

    producers=[
        # Get left and right side measurements
        # E.g.: ovaries: R 2 c. alb, L sev c. alb
        producer(double, r"""
            ovaries
                (?P<side_a> side)
                    (measurement | count)? (?P<value_a> (word)? luteum)
                (?P<side_b> side)
                    (measurement | count)? (?P<value_b> (word)? luteum)
            """),

        # One side may be reported
        # E.g.: left ovary=3x1.5mm, pale pink in color
        producer(
            convert,
            """(side)? ovaries
                (measurement)?
                (?P<value>
                    ( word | color | texture | luteum | state | size | and
                        | cyst ){0,3}
                    ( color | texture | luteum | state | size | cyst
                        | fallopian ))
            """),

        # Has the maturity but is possibly missing the size
        producer(
            convert,
            'ovaries (side)? (?P<value> (word){0,3} (size | state | luteum))'),

        # E.g.: large ovaries
        producer(convert, '(?P<value> (size | state | count){1,3} ) ovaries'),

        # E.g.: ovaries and uterine horns covered with copious fat
        producer(convert, 'ovaries (?P<value> coverage)'),

        # E.g.: reproductive data=Ovary, fallopian tubes dark red
        producer(convert, 'ovaries (?P<value> color | texture )'),

        # E.g.: +corp. alb both ovaries
        producer(convert, '(?P<value> luteum) (side)? ovaries'),

        # E.g.: ovaries L +lut
        producer(convert, 'ovaries (side)? luteum'),

        # E.g.: 4 bodies in L ovary
        producer(convert, '(?P<value> cyst ) (side)? ovaries'),

        # E.g.: corpus luteum visible in both ovaries
        producer(
            convert,
            """(?P<value> luteum (state)? )
                (word | len_units){0,3} (side)? ovaries
            """),
    ],
)