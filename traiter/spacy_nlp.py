"""A wrapper around spacy so we can use our rule-based parsers."""

import re

import spacy
from spacy.lang.char_classes import ALPHA, ALPHA_LOWER, ALPHA_UPPER, \
    CONCAT_QUOTES, HYPHENS, LIST_ELLIPSES, LIST_ICONS
from spacy.tokens import Span, Token

Token.set_extension('label', default='')
Token.set_extension('data', default={})
Token.set_extension('step', default='')
Token.set_extension('aux', default={})

Span.set_extension('label', default='')
Span.set_extension('data', default={})
Span.set_extension('step', default='')
Span.set_extension('aux', default={})


def spacy_nlp(
        disable=None,
        lang_model='en_core_web_sm',
        tokenizer=True,
        gpu='prefer'):
    """A single function to build the spacy nlp object for singleton use."""
    if gpu == 'prefer':
        spacy.prefer_gpu()
    elif gpu == 'require':
        spacy.require_gpu()

    if disable is None:
        disable = []

    nlp = spacy.load(lang_model, disable=disable)

    if tokenizer:
        setup_tokenizer(nlp)

    return nlp


def setup_tokenizer(nlp):
    """Setup custom tokenizer rules for the pipeline."""
    infix = (
            LIST_ELLIPSES
            + LIST_ICONS
            + [
                r"(?<=[0-9])[+\-\*^](?=[0-9])",
                r"(?<=[{al}{q}])\.(?=[{au}{q}])".format(
                    al=ALPHA_LOWER, au=ALPHA_UPPER, q=CONCAT_QUOTES),
                r"(?<=[{a}]),(?=[{a}])".format(a=ALPHA),
                # r"(?<=[{a}])(?:{h})(?=[{a}])".format(a=ALPHA, h=HYPHENS),
                r"(?<=[{a}0-9])[:<>=/+](?=[{a}])".format(a=ALPHA),
                r"""(?:{h})+""".format(h=HYPHENS),
                r"""[\\\[\]\(\)/:;"'+]""",
                r"(?<=[0-9])\.?(?=[{a}])".format(a=ALPHA),  # 1.word or 1N
            ])

    infix_regex = spacy.util.compile_infix_regex(infix)
    nlp.tokenizer.infix_finditer = infix_regex.finditer

    breaking = r"""[\[\]\\/()<>:;,.?"'+-]"""

    prefix = re.compile(f'^{breaking}')
    nlp.tokenizer.prefix_search = prefix.search

    suffix = re.compile(f'{breaking}$')
    nlp.tokenizer.suffix_search = suffix.search
