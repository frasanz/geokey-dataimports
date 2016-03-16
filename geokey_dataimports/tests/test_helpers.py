"""All tests for context helpers."""

from django.test import TestCase

from ..helpers.context_helpers import does_not_exist_msg
from ..helpers.type_helpers import is_numeric, is_date, is_time


class DoesNotExistMsgTest(TestCase):
    """Test does_not_exist_msg method."""

    def test_method_with_project(self):
        """Test with `Project`."""
        self.assertEqual(
            does_not_exist_msg('Project'),
            'Project matching query does not exist.'
        )

    def test_method_with_category(self):
        """Test with `Category`."""
        self.assertEqual(
            does_not_exist_msg('Category'),
            'Category matching query does not exist.'
        )

    def test_method_with_dataimport(self):
        """Test with `Data import`."""
        self.assertEqual(
            does_not_exist_msg('Data import'),
            'Data import matching query does not exist.'
        )


class IsNumericTest(TestCase):
    """Test is_numeric method."""

    def test_method_with_empty_input(self):
        """Test with empty input."""
        self.assertFalse(is_numeric())
        self.assertFalse(is_numeric(''))

    def test_method_with_text(self):
        """Test with text."""
        self.assertFalse(is_numeric('London is great.'))

    def test_method_with_well_known_text(self):
        """Test with well-known text."""
        self.assertFalse(
            is_numeric('POINT (30 10)')
        )
        self.assertFalse(
            is_numeric('LINESTRING (30 10, 10 30, 40 40)')
        )
        self.assertFalse(
            is_numeric('POLYGON ((30 10, 40 40, 20 40, 10 20, 30 10))')
        )

    def test_method_with_number(self):
        """Test with number."""
        self.assertTrue(is_numeric(29))
        self.assertTrue(is_numeric('29'))

    def test_method_with_date(self):
        """Test with date."""
        self.assertFalse(is_numeric('2014-09-21T15:51:32'))
        self.assertFalse(is_numeric('2014-09-21T15:51:32.804Z'))

    def test_method_with_time(self):
        """Test with time."""
        self.assertFalse(is_numeric('10:12'))
        self.assertFalse(is_numeric('23:14'))


class IsDateTest(TestCase):
    """Test is_date method."""

    def test_method_with_empty_input(self):
        """Test with empty input."""
        self.assertFalse(is_date())
        self.assertFalse(is_date(''))

    def test_method_with_text(self):
        """Test with text."""
        self.assertFalse(is_date('London is great.'))

    def test_method_with_well_known_text(self):
        """Test with well-known text."""
        self.assertFalse(
            is_date('POINT (30 10)')
        )
        self.assertFalse(
            is_date('LINESTRING (30 10, 10 30, 40 40)')
        )
        self.assertFalse(
            is_date('POLYGON ((30 10, 40 40, 20 40, 10 20, 30 10))')
        )

    def test_method_with_number(self):
        """Test with number."""
        self.assertFalse(is_date(29))
        self.assertFalse(is_date('29'))

    def test_method_with_date(self):
        """Test with date."""
        self.assertTrue(is_date('2014-09-21T15:51:32'))
        self.assertTrue(is_date('2014-09-21T15:51:32.804Z'))

    def test_method_with_time(self):
        """Test with time."""
        self.assertFalse(is_date('5:12'))
        self.assertFalse(is_date('23:14'))


class IsTimeTest(TestCase):
    """Test is_time method."""

    def test_method_with_empty_input(self):
        """Test with empty input."""
        self.assertFalse(is_time())
        self.assertFalse(is_time(''))

    def test_method_with_text(self):
        """Test with text."""
        self.assertFalse(is_time('London is great.'))

    def test_method_with_well_known_text(self):
        """Test with well-known text."""
        self.assertFalse(
            is_time('POINT (30 10)')
        )
        self.assertFalse(
            is_time('LINESTRING (30 10, 10 30, 40 40)')
        )
        self.assertFalse(
            is_time('POLYGON ((30 10, 40 40, 20 40, 10 20, 30 10))')
        )

    def test_method_with_number(self):
        """Test with number."""
        self.assertFalse(is_time(29))
        self.assertFalse(is_time('29'))

    def test_method_with_date(self):
        """Test with date."""
        self.assertFalse(is_time('2014-09-21T15:51:32'))
        self.assertFalse(is_time('2014-09-21T15:51:32.804Z'))

    def test_method_with_time(self):
        """Test with time."""
        self.assertTrue(is_time('5:12'))
        self.assertTrue(is_time('23:14'))
