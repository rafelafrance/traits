"""Test the parser's scan function."""

import unittest
from traiter.rule import part
from traiter.token import Token
from traiter.parser import Parser


class TestScan(unittest.TestCase):
    """Test the parser's scan function."""

    r_dog = part('dog', ' doggie dog '.split())
    r_cat = part('cat', ' bearcat cat '.split())

    def test_scan_01(self):
        """It finds a match."""
        parser = Parser([self.r_dog])
        parser.build()
        self.assertEqual(
            parser.scan('dogs'),
            [Token(self.r_dog, span=(0, 3), group={'dog': 'dog'})])

    def test_scan_02(self):
        """It compares with another token object."""
        parser = Parser([self.r_dog])
        parser.build()
        self.assertEqual(parser.scan('dogs'), parser.scan('dogs'))

    def test_scan_03(self):
        """It finds multiple tokens."""
        parser = Parser([self.r_dog])
        parser.build()
        self.assertEqual(
            parser.scan('doggie dogs'),
            [Token(self.r_dog, span=(0, 6), group={'dog': 'doggie'}),
             Token(self.r_dog, span=(7, 10), group={'dog': 'dog'})])

    def test_scan_04(self):
        """It skips strings that are part of a previous token."""
        parser = Parser([self.r_cat])
        parser.build()
        self.assertEqual(
            parser.scan('bearcat cats'),
            [Token(self.r_cat, span=(0, 7), group={'cat': 'bearcat'}),
             Token(self.r_cat, span=(8, 11), group={'cat': 'cat'})])