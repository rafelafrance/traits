"""Parse ovaries size notations."""

from pylib.stacked_regex.rule_catalog import RuleCatalog
from pylib.vertnet.reproductive import double, convert
from pylib.vertnet.parsers.base import Base
import pylib.vertnet.shared_reproductive_patterns as patterns


CATALOG = RuleCatalog(patterns.CATALOG)


OVARY_SIZE = Base(
    name=__name__.split('.')[-1],
    rules=[
        # A key with units, like: gonadLengthInMM
        CATALOG.term('key_with_units', r"""
            (?P<ambiguous_key> gonad ) \s*
                (?P<dim> length | len | width ) \s* in \s*
                (?P<len_units> millimeters | mm )
            """),

        CATALOG.grouper('value', ' cross | number len_units? '),

        # E.g.: active
        # Or:   immature
        CATALOG.grouper(
            'state', 'active mature destroyed visible developed'.split()),

        # Male or female ambiguous, like: gonadLength1
        CATALOG.grouper('ambiguous', """
            ambiguous_key dim_side
            | side ambiguous_key dimension
            | ambiguous_key dimension """),

        # These patterns contain measurements to both left & right ovaries
        # E.g.: reproductive data: ovaries left 10x5 mm, right 10x6 mm
        CATALOG.producer(double, """ label ovary side_cross """),

        # As above but without the ovaries marker:
        # E.g.: reproductive data: left 10x5 mm, right 10x6 mm
        CATALOG.producer(double, """label side_cross"""),

        # Has side before gonad key
        # E.g.: left ovary: 4 x 2 mm
        CATALOG.producer(double, """ side_cross """),

        # Has the ovaries marker but is lacking the label
        # E.g.: ovaries left 10x5 mm, right 10x6 mm
        CATALOG.producer(double, """ ovary side_cross """),

        # A typical testes size notation
        # E.g.: reproductive data: ovaries 10x5 mm
        CATALOG.producer(convert, ' label ovary value '),

        # E.g.: reproductive data: left ovaries 10x5 mm
        CATALOG.producer(convert, ' label side ovary value '),

        # E.g.: left ovaries 10x5 mm
        CATALOG.producer(convert, ' side ovary value '),

        # E.g.: reproductive data: 10x5 mm
        CATALOG.producer(convert, 'label value'),

        # May have a few words between the label and the measurement
        CATALOG.producer(convert, """
            label ( ovary | state | word | sep ){0,3}
            ( ovary | state ) value"""),

        # Handles: gonadLengthInMM 4x3
        # And:     gonadLength 4x3
        CATALOG.producer(convert, '( ambiguous | key_with_units ) value'),

        # E.g.: gonadLengthInMM 6 x 8
        CATALOG.producer(convert, """
            ( key_with_units | ambiguous )
            ( ovary | state | word | sep ){0,3}
            ( ovary | state ) value"""),

        # Anchored by ovaries but with words between
        CATALOG.producer(
            convert, 'ovary ( state | word | sep ){0,3} state value'),

        # Anchored by ovaries but with only one word in between
        # E.g.: ovaries scrotal 9mm
        CATALOG.producer(convert, 'side? ovary ( state | word ) value'),

        # E.g.: Ovaries 5 x 3
        CATALOG.producer(convert, 'side? ovary value'),
    ],
)
