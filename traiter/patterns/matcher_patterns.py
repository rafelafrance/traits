"""Compile strings to spacy matcher patterns.

EXPERIMENTAL!

In an effort to make patterns more readable I've created simple compilers that take in,
hopefully, readable strings and convert them to spacy patterns using a dictionary and
some simple rules.
"""

from copy import deepcopy
from typing import Callable, Union
from warnings import warn

from spacy import registry
from spacy.pipeline import EntityRuler
from spacy.tokens import Span


class MatcherPatterns:
    """Pattern object for rule-based matchers."""

    def __init__(
            self,
            label: str,
            *,
            patterns: Union[str, list[Union[str, list[dict]]]],
            decoder: Union[dict[str, dict], None] = None,
            on_match: Union[Callable[[Span], None], str, None] = None,
            id_: str = ''):
        self.label = label
        self.decoder = decoder
        self.on_match = on_match
        self.patterns = patterns
        self.id = id_

        if decoder:
            patterns = patterns if isinstance(patterns, list) else [patterns]
            self.patterns = self.compile(patterns)

        if callable(on_match):
            registry.misc.register(name=label, func=on_match)
            self.on_match = label

    def as_dict(self) -> dict:
        """Return the object as a serializable dict."""
        return {
            'label': self.label,
            'on_match': self.on_match,
            'patterns': self.patterns,
            'id': self.id,
        }

    def compile(self, patterns: list[str]) -> list[list[dict]]:
        """Convert patterns strings to spacy matcher pattern arrays."""
        all_patterns = []

        for string in patterns:
            pattern_seq = []

            for key in string.split():
                token = deepcopy(self.decoder.get(key))
                op = key[-1]

                if not token and op in '?*+!':
                    token = deepcopy(self.decoder.get(key[:-1]))
                    token['OP'] = op

                if token:
                    pattern_seq.append(token)
                else:
                    warn(f'No token pattern for "{key}" in "{string}"')

            all_patterns.append(pattern_seq)

        return all_patterns


def as_dicts(patterns: list[MatcherPatterns]) -> list[dict]:
    """Convert all patterns to a dicts."""
    return [p.as_dict() for p in patterns]


def add_ruler_patterns(ruler: EntityRuler, patterns: list[MatcherPatterns]) -> None:
    """Add patterns to a ruler."""
    rules = []
    for matcher in patterns:
        label = matcher.label
        id_ = matcher.id
        for pattern in matcher.patterns:
            rule = {'label': label, 'pattern': pattern}
            if id_:
                rule['id'] = id_
            rules.append(rule)
    ruler.add_patterns(rules)
