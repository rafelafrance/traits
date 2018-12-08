"""Lex sex annotations."""

# pylint: disable=too-few-public-methods

from lib.lexers.base_lexer import BaseLexer, build


class SexLexer(BaseLexer):
    """Lex testes state annotations."""

    tokens = [
        BaseLexer.stop,  # We don't want to confuse prefix and suffix notation

        ('key', build(r' sex ')),

        ('sex', build(r' males? | females? ')),

        ('quest', r' \? '),

        # These are words that indicate "sex" is not a key
        ('skip', build(r' and | was | is ')),

        BaseLexer.word]