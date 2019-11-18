"""Parse lactation state notations."""

from pylib.stacked_regex.rule import fragment, producer, replacer
from pylib.vertnet.parsers.base import Base, convert
from pylib.vertnet.shared_reproductive_patterns import REPRODUCTIVE


LACTATION_STATE = Base(
    name=__name__.split('.')[-1],
    scanners=[
        fragment('lactating', r""" (
            lactating | lactation | lactated | lactate | lact
            | lactaing | lactacting | lactataing | lactational
            | oelact | celact | lactati | lactacting | lactatin
            | lactatting | lactatng
            | nursing | suckling
        ) \b """),

        fragment('not', r' \b ( not | non | no ) '),

        fragment('post', r""" \b (
            (( just | recently ) \s+ )? finished
            | post | recently | recent | had | pre
        ) """),

        # To handle a guessed trait
        fragment('quest', '[?]'),

        # Separates measurements
        fragment('separator', r' [;"/] '),

        REPRODUCTIVE['word'],
    ],

    replacers=[
        replacer('prefix', 'not post'.split()),
    ],

    producers=[
        producer(convert, """ (?P<value> prefix? lactating quest? ) """),
    ],
)