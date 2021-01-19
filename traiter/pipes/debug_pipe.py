"""Add a pipe to print debug messages."""

from spacy.language import Language


@Language.component('debug_tokens')
def debug_tokens(doc):
    """Print debug messages."""
    print('=' * 80)
    print('debug_tokens')
    for token in doc:
        print(f'{token.ent_type_:<20} {token}')
    print()
    return doc


@Language.component('debug_entities')
def debug_entities(doc):
    """Print debug messages."""
    print('=' * 80)
    print('debug_entities')
    for ent in doc.ents:
        print(f'{ent.label_:<20} {ent}')
    print()
    return doc