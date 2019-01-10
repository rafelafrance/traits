# flake8=noqa

import unittest
from lib.parsed_trait import ParsedTrait
from lib.traits.life_stage import LifeStage


PAR = LifeStage()


class TestLifeStage(unittest.TestCase):

    def test_parse_01(self):
        self.assertEqual(
            PAR.parse('sex=unknown ; age class=adult/juvenile after'),
            [ParsedTrait(value='adult / juvenile', start=14, end=38)])

    def test_parse_02(self):
        self.assertEqual(
            PAR.parse('age=u ad.'),
            [ParsedTrait(value='u ad', start=0, end=8)])

    def test_parse_03(self):
        self.assertEqual(
            PAR.parse(
                'weight=5.2 g; age class=over-winter ; total length=99 mm;0'),
            [ParsedTrait(value='over-winter', start=14, end=37)])

    def test_parse_04(self):
        self.assertEqual(
            PAR.parse(
                'sex=female ? ; age=1st year more than four words here'),
            [ParsedTrait(value='1st year', start=15, end=27)])

    def test_parse_05(self):
        self.assertEqual(
            PAR.parse('words after hatching year more words'),
            [ParsedTrait(value='after hatching year', start=6, end=25)])

    def test_parse_06(self):
        self.assertEqual(
            PAR.parse('age determined by 20-sided die'),
            [])

    def test_parse_07(self):
        self.assertEqual(
            PAR.parse('LifeStage Remarks: 5-6 wks;'),
            [ParsedTrait(value='5-6 wks', start=0, end=27)])

    def test_parse_08(self):
        self.assertEqual(
            PAR.parse('mentions juvenile'),
            [ParsedTrait(value='juvenile', start=9, end=17)])

    def test_parse_09(self):
        self.assertEqual(
            PAR.parse('mentions juveniles in the field'),
            [ParsedTrait(value='juveniles', start=9, end=18)])

    def test_parse_10(self):
        self.assertEqual(
            PAR.parse('one or more adults'),
            [ParsedTrait(value='adults', start=12, end=18)])

    def test_parse_11(self):
        self.assertEqual(
            PAR.parse('adults'),
            [ParsedTrait(value='adults', start=0, end=6)])

    def test_parse_12(self):
        self.assertEqual(
            PAR.parse('Adulte'),
            [ParsedTrait(value='adulte', start=0, end=6)])

    def test_parse_13(self):
        self.assertEqual(
            PAR.parse('AGE IMM'),
            [ParsedTrait(value='imm', start=0, end=7)])

    def test_parse_14(self):
        self.assertEqual(
            PAR.parse('subadult'),
            [ParsedTrait(value='subadult', start=0, end=8)])

    def test_parse_15(self):
        self.assertEqual(
            PAR.parse('subadultery'),
            [])

    def test_parse_16(self):
        self.assertEqual(
            PAR.parse('in which larvae are found'),
            [ParsedTrait(value='larvae', start=9, end=15)])

    def test_parse_17(self):
        self.assertEqual(
            PAR.parse('one tadpole'),
            [ParsedTrait(value='tadpole', start=4, end=11)])

    def test_parse_18(self):
        # Lifestage removed
        self.assertEqual(
            PAR.parse('some embryos'),
            [])

    def test_parse_19(self):
        self.assertEqual(
            PAR.parse('young adult'),
            [ParsedTrait(value='young adult', start=0, end=11)])

    def test_parse_20(self):
        self.assertEqual(
            PAR.parse('adult young'),
            [ParsedTrait(value='adult', start=0, end=5),
             ParsedTrait(value='young', start=6, end=11)])

    def test_parse_21(self):
        self.assertEqual(
            PAR.parse('sub-adult'),
            [ParsedTrait(value='sub-adult', start=0, end=9)])

    def test_parse_22(self):
        self.assertEqual(
            PAR.parse('adult(s) and juvenile(s)'),
            [ParsedTrait(value='adult', start=0, end=5),
             ParsedTrait(value='juvenile', start=13, end=21)])

    def test_parse_23(self):
        self.assertEqual(
            PAR.parse('young-of-the-year'),
            [ParsedTrait(value='young-of-the-year', start=0, end=17)])

    def test_parse_24(self):
        self.assertEqual(
            PAR.parse('YOLK SAC'),
            [ParsedTrait(value='yolk sac', start=0, end=8)])
