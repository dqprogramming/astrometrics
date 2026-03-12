"""
Tests for the pure parsing functions in the import_journals command.

These functions have no database dependencies and can be tested
with SimpleTestCase.
"""

from decimal import Decimal

from django.test import SimpleTestCase

from journals.management.commands.import_journals import Command


class ParseDecimalTests(SimpleTestCase):
    """Tests for Command._parse_decimal."""

    def setUp(self):
        self.cmd = Command()

    def test_plain_number(self):
        self.assertEqual(self.cmd._parse_decimal("5000"), Decimal("5000"))

    def test_decimal_places(self):
        self.assertEqual(
            self.cmd._parse_decimal("5000.50"), Decimal("5000.50")
        )

    def test_pound_sign(self):
        self.assertEqual(self.cmd._parse_decimal("£5000"), Decimal("5000"))

    def test_comma_separated(self):
        self.assertEqual(self.cmd._parse_decimal("5,000"), Decimal("5000"))

    def test_pound_and_comma(self):
        self.assertEqual(
            self.cmd._parse_decimal("£5,000.50"), Decimal("5000.50")
        )

    def test_whitespace(self):
        self.assertEqual(self.cmd._parse_decimal("  5000  "), Decimal("5000"))

    def test_empty_string(self):
        self.assertIsNone(self.cmd._parse_decimal(""))

    def test_none(self):
        self.assertIsNone(self.cmd._parse_decimal(None))

    def test_non_string(self):
        self.assertIsNone(self.cmd._parse_decimal(123))

    def test_invalid_string(self):
        self.assertIsNone(self.cmd._parse_decimal("not a number"))

    def test_zero(self):
        self.assertEqual(self.cmd._parse_decimal("0"), Decimal("0"))

    def test_negative(self):
        self.assertEqual(self.cmd._parse_decimal("-100"), Decimal("-100"))


class ParseIntegerTests(SimpleTestCase):
    """Tests for Command._parse_integer."""

    def setUp(self):
        self.cmd = Command()

    def test_plain_integer(self):
        self.assertEqual(self.cmd._parse_integer("10"), 10)

    def test_zero(self):
        self.assertEqual(self.cmd._parse_integer("0"), 0)

    def test_whitespace(self):
        self.assertEqual(self.cmd._parse_integer("  10  "), 10)

    def test_empty_string(self):
        self.assertIsNone(self.cmd._parse_integer(""))

    def test_none(self):
        self.assertIsNone(self.cmd._parse_integer(None))

    def test_non_string(self):
        self.assertIsNone(self.cmd._parse_integer(123))

    def test_float_string(self):
        self.assertIsNone(self.cmd._parse_integer("10.5"))

    def test_invalid_string(self):
        self.assertIsNone(self.cmd._parse_integer("abc"))

    def test_negative(self):
        self.assertEqual(self.cmd._parse_integer("-5"), -5)


class ParseBooleanTests(SimpleTestCase):
    """Tests for Command._parse_boolean."""

    def setUp(self):
        self.cmd = Command()

    def test_y(self):
        self.assertTrue(self.cmd._parse_boolean("Y"))

    def test_yes(self):
        self.assertTrue(self.cmd._parse_boolean("YES"))

    def test_true(self):
        self.assertTrue(self.cmd._parse_boolean("TRUE"))

    def test_one(self):
        self.assertTrue(self.cmd._parse_boolean("1"))

    def test_lowercase_y(self):
        self.assertTrue(self.cmd._parse_boolean("y"))

    def test_lowercase_yes(self):
        self.assertTrue(self.cmd._parse_boolean("yes"))

    def test_mixed_case(self):
        self.assertTrue(self.cmd._parse_boolean("Yes"))

    def test_n(self):
        self.assertFalse(self.cmd._parse_boolean("N"))

    def test_no(self):
        self.assertFalse(self.cmd._parse_boolean("NO"))

    def test_false(self):
        self.assertFalse(self.cmd._parse_boolean("FALSE"))

    def test_empty_string(self):
        self.assertFalse(self.cmd._parse_boolean(""))

    def test_none(self):
        self.assertFalse(self.cmd._parse_boolean(None))

    def test_whitespace_y(self):
        self.assertTrue(self.cmd._parse_boolean("  Y  "))

    def test_arbitrary_string(self):
        self.assertFalse(self.cmd._parse_boolean("maybe"))


class ParseLicenseTests(SimpleTestCase):
    """Tests for Command._parse_license."""

    def setUp(self):
        self.cmd = Command()

    def test_cc_by(self):
        self.assertEqual(self.cmd._parse_license("CC BY"), "CC BY")

    def test_cc_by_nc(self):
        self.assertEqual(self.cmd._parse_license("CC BY-NC"), "CC BY-NC")

    def test_cc_by_nc_sa(self):
        self.assertEqual(self.cmd._parse_license("CC BY-NC-SA"), "CC BY-NC-SA")

    def test_cc_by_nc_nd(self):
        self.assertEqual(self.cmd._parse_license("CC BY-NC-ND"), "CC BY-NC-ND")

    def test_cc_by_sa(self):
        self.assertEqual(self.cmd._parse_license("CC BY-SA"), "CC BY-SA")

    def test_cc_by_nd(self):
        self.assertEqual(self.cmd._parse_license("CC BY-ND"), "CC BY-ND")

    def test_unknown_license_passed_through(self):
        self.assertEqual(self.cmd._parse_license("MIT License"), "MIT License")

    def test_empty_string(self):
        self.assertEqual(self.cmd._parse_license(""), "")

    def test_none(self):
        self.assertEqual(self.cmd._parse_license(None), "")

    def test_whitespace_stripped(self):
        self.assertEqual(self.cmd._parse_license("  CC BY  "), "CC BY")
