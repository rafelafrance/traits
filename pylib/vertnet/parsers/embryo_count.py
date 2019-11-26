"""Parse embryo counts."""

from pylib.stacked_regex.rule import fragment, producer, grouper
from pylib.shared.util import as_list, to_int
from pylib.vertnet.parsers.base import Base
from pylib.vertnet.trait import Trait
from pylib.vertnet.shared_reproductive_patterns import RULE


SUB = {'l': 'left', 'r': 'right', 'm': 'male', 'f': 'female'}


def convert(token):
    """Convert parsed tokens into a result."""
    trait = Trait(start=token.start, end=token.end)

    if token.groups.get('total'):
        trait.value = to_int(token.groups['total'])

    elif token.groups.get('subcount'):
        trait.value = sum(
            to_int(c) for c in as_list(token.groups['subcount']))

    if token.groups.get('subcount') and token.groups.get('sub'):
        for count, sub in zip(as_list(token.groups['subcount']),
                              as_list(token.groups.get('sub'))):
            sub = SUB.get(sub[0].lower(), sub)
            setattr(trait, sub, to_int(count))

    if trait.value > 1000:
        return None

    return trait


EMBRYO_COUNT = Base(
    name=__name__.split('.')[-1],
    rules=[
        RULE['uuid'],  # UUIDs cause problems with shorthand
        RULE['embryo'],
        RULE['size'],
        RULE['fat'],
        RULE['integer'],
        RULE['side'],
        RULE['none'],
        RULE['conj'],
        RULE['prep'],

        # The sexes like: 3M or 4Females
        fragment('sex', r"""
            males? | females? | (?<! [a-z] ) [mf] (?! [a-z] ) """),

        RULE['sep'],

        # Skip arbitrary words
        RULE['word'],

        grouper('count', ' none word conj | integer | none '),

        producer(convert, """
            ( (?P<total> count) word? )?
            embryo ((integer (?! side) ) | word)*
            (?P<subcount> count) (?P<sub> side | sex)
            ( ( conj | prep )? (?P<subcount> count) (?P<sub> side | sex) )?
            """),

        # Eg: 4 fetuses on left, 1 on right
        producer(convert, [
            """ (?P<subcount> count ) embryo prep? (?P<sub> side )
                (?P<subcount> count ) embryo? prep? (?P<sub> side )"""]),

        producer(convert, """
            (?P<total> count) (size | word)? embryo """),
    ],
)
