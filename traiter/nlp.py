"""A wrapper around spacy so we can use our rule-based parsers."""

import regex
import spacy
from spacy.lang.char_classes import ALPHA, ALPHA_LOWER, ALPHA_UPPER, \
    CONCAT_QUOTES, HYPHENS, LIST_ELLIPSES, LIST_ICONS, PUNCT
from spacy.tokens import Token  # Doc, Span


def canon(token):
    """Lower case the string & remove noise characters."""
    text = token.text.lower()
    if not (token.is_punct or token.like_num):
        text = regex.sub(r'\p{Dash_Punctuation}', '', text)
    return text


# Token.set_extension('canon', getter=canon)
Token.set_extension('term', default='')


def spacy_nlp():
    """A single function to build the spacy nlp object for singleton use."""
    spacy.prefer_gpu()
    nlp = spacy.load('en_core_web_sm', disable=['parser', 'ner'])

    infix = (
        LIST_ELLIPSES
        + LIST_ICONS
        + [
            r"(?<=[0-9])[+\-\*^](?=[0-9-])",
            r"(?<=[{al}{q}])\.(?=[{au}{q}])".format(
                al=ALPHA_LOWER, au=ALPHA_UPPER, q=CONCAT_QUOTES),
            r"(?<=[{a}]),(?=[{a}])".format(a=ALPHA),
            # r"(?<=[{a}])(?:{h})(?=[{a}])".format(a=ALPHA, h=HYPHENS),
            r"(?<=[{a}0-9])[:<>=/](?=[{a}])".format(a=ALPHA),

            ###############################################
            # Custom interior rules

            r"""(?:{h})""".format(h=HYPHENS),
            r"""[:"=()\[\]]""",
            r"(?<=[0-9])\.(?=[{a}])".format(a=ALPHA),  # 1.word, 2.other
            ])
    infix_regex = spacy.util.compile_infix_regex(infix)
    nlp.tokenizer.infix_finditer = infix_regex.finditer
    return nlp


NLP = spacy_nlp()
