"""Parse body mass notations."""

from pyparsing import Regex, Word, alphas, alphanums
from lib.parsers.base import Base, Result
import lib.parsers.regexp as rx
from lib.parsers.convert_units import convert


class TotalLength(Base):
    """Parser logic."""

    def build_parser(self):
        """Return the trait parser."""
        words = Word(alphas, alphanums)*(1, 3)

        key_with_units = Regex(r"""
            total  [\s-]* length [\s-]* in [\s-]* (?: mm | millimeters)
            | length [\s-]* in [\s-]* (?: mm | millimeters)
            | snout [\s-]* vent [\s-]* lengths? [\s-]* in [\s-]*
                (?: mm | millimeters)
            | head  [\s-]* body [\s-]* length [\s-]* in [\s-]*
                (?: mm | millimeters)
            """, rx.flags)

        len_key = Regex(r"""
            total  [\s-]* length [\s-]* in
            | (?: total | max | standard ) [\s-]* lengths?
            | meas [\s*:]? \s* length [\s(]* [l] [)\s:]*
            | meas (?: [a-z]* )? \.? : \s* L
            | t [o.]? l \.? _?
            | s \.? l \.?
            | label [\s.]* lengths?
            | (?: fork | mean | body ) [\s-]* lengths?
            | s \.? v \.? ( l \.? )?
            | snout [\s-]* vent [\s-]* lengths?
            """, rx.flags)

        ambiguous = Regex(r'(?<! [a-z] )(?<! [a-z] \s ) lengths? ', rx.flags)
        key_units_req = Regex(r'measurements? | body | total', rx.flags)

        parser = (
            key_with_units('millimeters') + rx.range

            | rx.shorthand_key + rx.range + rx.len_units
            | rx.shorthand_key + rx.len_units + rx.range

            | key_units_req + rx.fraction + rx.len_units
            | key_units_req + rx.range + rx.len_units

            | len_key + rx.fraction + rx.len_units
            | (ambiguous + rx.fraction + rx.len_units).setParseAction(
                self.ambiguous)


            | rx.range + rx.len_units + len_key
            | rx.range + len_key

            | (len_key
               + rx.range('ft') + rx.feet
               + rx.range('in') + rx.inches)
            | (rx.range('ft') + rx.feet
               + rx.range('in') + rx.inches).setParseAction(self.ambiguous)

            # Due to trailing len_key the leading key it is no longer ambiguous
            | ambiguous + rx.range + rx.len_units + len_key
            | ambiguous + rx.range + len_key

            | (ambiguous + rx.range + rx.len_units).setParseAction(
                self.ambiguous)
            | (ambiguous + rx.len_units + rx.range).setParseAction(
                self.ambiguous)
            | (ambiguous + rx.range).setParseAction(self.ambiguous)

            | rx.shorthand_key + rx.shorthand
            | rx.shorthand

            | len_key + rx.range + rx.len_units
            | len_key + rx.len_units + rx.range
            | len_key + rx.range
            | len_key + words + rx.range + rx.len_units
            | len_key + words + rx.range
        )

        ignore = Word(rx.punct, excludeChars=';')
        parser.ignore(ignore)
        return parser

    @staticmethod
    def ambiguous(tokens):
        """Flag an ambiguous parse."""
        return tokens.append('ambiguous')

    def result(self, match):
        """Convert parsed tokens into a result."""
        parts = match[0].asDict()

        if parts.get('shorthand_tl') is not None:
            return self.shorthand(match, parts)
        if parts.get('ft') is not None:
            return self.english(match, parts)
        if parts.get('numerator') is not None:
            return self.fraction(match, parts)

        ambiguous = 'ambiguous' in match[0].asList()

        units = parts.get('units')
        if parts.get('millimeters'):
            units = 'mm'
        has_units = bool(units)

        value = self.to_float(parts['value1'])
        value2 = self.to_float(parts['value2'])
        if value2:
            value = [value, value2]
        value = convert(value, units)

        return Result(value=value,
                      has_units=has_units,
                      ambiguous=ambiguous,
                      start=match[1], end=match[2])

    def shorthand(self, match, parts):
        """Handle shorthand notation like 11-22-33-44:55g."""
        value = self.to_float(parts.get('shorthand_tl'))
        if not value:
            return None
        return Result(value=value,
                      has_units=True,
                      start=match[1], end=match[2])

    def english(self, match, parts):
        """Handle a pattern like: 4 lbs 9 ozs."""
        ambiguous = 'ambiguous' in match[0].asList()
        lbs = self.to_floats(parts['ft'], rx.range_joiner)
        ozs = self.to_floats(parts['in'], rx.range_joiner)
        value = [convert(x, 'ft') + convert(y, 'in')
                 for x in lbs for y in ozs]

        if len(value) == 1:
            value = value[0]

        return Result(value=value,
                      ambiguous=ambiguous,
                      has_units=True,
                      start=match[1], end=match[2])

    def fraction(self, match, parts):
        """Handle fractional values like 10 3/8 inches."""
        ambiguous = 'ambiguous' in match[0].asList()

        units = parts.get('units')
        has_units = bool(units)

        whole = self.to_float(parts['whole'])
        whole = whole if whole else 0
        numerator = self.to_float(parts['numerator'])
        denominator = self.to_float(parts['denominator'])
        value = convert(whole + numerator / denominator, units)

        return Result(
            value=value,
            ambiguous=ambiguous,
            has_units=has_units,
            start=match[1], end=match[2])
