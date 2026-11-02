import unittest
from average import average


class AverageTests(unittest.TestCase):
    def test_simple(self):
        self.assertEqual(average([2, 4]), 3)

    def test_empty(self):
        self.assertIsNone(average([]))

    def test_singleton(self):
        self.assertEqual(average([7]), 7)

    def test_mixed_sign(self):
        self.assertEqual(average([-5, 2, 9]), 2)

    def test_decimal(self):
        self.assertAlmostEqual(average([0.1, 0.2, 0.6]), 0.3)
