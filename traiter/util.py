"""Misc. utilities shared between client Traiters."""

import os
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from shutil import rmtree
from tempfile import TemporaryDirectory, mkdtemp
from typing import Any, Hashable, List, Optional, Set, Tuple, Union

import ftfy
import inflect
import regex as re

__VERSION__ = '0.8.5'

# This points to the client's data directory
DATA_DIR = Path.cwd() / 'data'

# Default term step
TERM_STEP = 'terms'

FLAGS = re.VERBOSE | re.IGNORECASE

BATCH_SIZE = 1_000_000  # How many records to work with at a time

INFLECT = inflect.engine()


class DotDict(dict):
    """Allow dot.notation access to dictionary items."""

    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


def log(msg: str) -> None:
    """Log a status message."""
    print(f'{now()} {msg}')


def now() -> str:
    """Generate a timestamp."""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def today() -> str:
    """Get today's date."""
    return now()[:10]


@contextmanager
def get_temp_dir(
        prefix: str = 'temp_',
        where: Optional[Union[str, Path]] = None,
        keep: bool = False
) -> TemporaryDirectory:
    """Handle creation and deletion of temporary directory."""
    if where and not os.path.exists(where):
        os.mkdir(where)

    temp_dir = mkdtemp(prefix=prefix, dir=where)

    try:
        yield temp_dir
    finally:
        if not keep or not where:
            rmtree(temp_dir)


def shorten(text: str) -> str:
    """Collapse whitespace in a string."""
    return ' '.join(text.split())


def flatten(nested: Any) -> List:
    """Flatten an arbitrarily nested list."""
    flat = []
    nested = nested if isinstance(nested, (list, tuple, set)) else [nested]
    for item in nested:
        # if not isinstance(item, str) and hasattr(item, '__iter__'):
        if isinstance(item, (list, tuple, set)):
            flat.extend(flatten(item))
        else:
            flat.append(item)
    return flat


def squash(values: Union[List, Set]) -> Any:
    """Squash a list to a single value is its length is one."""
    return list(values) if len(values) != 1 else values.pop()


def as_list(values: Any) -> List:
    """Convert values to a list."""
    return list(values) if isinstance(values, (list, tuple, set)) else [values]


def as_set(values: Any) -> Set:
    """Convert values to a list."""
    return set(values) if isinstance(values, (list, tuple, set)) else {values}


def as_tuple(values: Any) -> Tuple:
    """Convert values to a tuple."""
    return values if isinstance(values, (list, tuple, set)) else (values,)


def as_member(values: Any) -> Hashable:
    """Convert values to set members (hashable)."""
    return tuple(values) if isinstance(values, (list, set)) else values


def to_positive_float(value: str):
    """Convert the value to a float."""
    value = re.sub(r'[^\d./]', '', value) if value else ''
    try:
        return float(value)
    except ValueError:
        return None


def to_positive_int(value: str):
    """Convert the value to an integer."""
    value = re.sub(r'[^\d./]', '', value) if value else ''
    value = re.sub(r"\.$", '', value)
    try:
        return int(value)
    except ValueError:
        return None


def camel_to_snake(name: str) -> str:
    """Convert a camel case string to snake case."""
    split = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', split).lower()


def ordinal(i: str) -> str:
    """Convert the digit to an ordinal value: 1->1st, 2->2nd, etc."""
    return INFLECT.ordinal(i)


def number_to_words(number: str) -> str:
    """Convert the number or ordinal value into words."""
    return INFLECT.number_to_words(number)


def clean_text(text: str, trans: Optional[str.translate] = None) -> str:
    """Strip control characters from improperly encoded input strings."""
    text = text if text else ''
    if trans:
        text = text.translate(trans)  # Handle uncommon mojibake
    text = text.replace('\f', '\n\n')  # replace form feeds
    # text = ' '.join(text.split())  # Space normalize
    # Join hyphenated words when they are at the end of a line
    # text = re.sub(r'([a-z])-\s+([a-z])', r'\1\2', text, flags=re.IGNORECASE)
    text = ftfy.fix_text(text)  # Handle common mojibake
    text = re.sub(r'\p{Cc}+', ' ', text)  # Remove control characters
    return text


def xor(one: Any, two: Any) -> bool:
    """Emulate a logical xor."""
    return (one and two) or (not one and not two)


def filter_matches(matches: List[Tuple]) -> List[Tuple]:
    """Filter a sequence of matches so they don't contain overlaps.

    This is a counterpart to spacy's filter_spans() function.
    Matches: array of tuples: [(match_id, start, end), ...]
    """
    if not matches:
        return []
    first, *rest = sorted(matches, key=lambda m: (m[1], -m[2]))
    cleaned = [first]
    for match in rest:
        if match[1] >= cleaned[-1][2]:
            cleaned.append(match)
    return cleaned
