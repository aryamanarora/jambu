"""Checks for the new analysis choices, independent of the corpus snapshot."""
import unittest
from extensions import age, dist, unilateral


class ExtensionTests(unittest.TestCase):
    def test_plains_fragmentation_does_not_change_one_sided_score(self):
        d = {'a': 1}
        self.assertEqual(unilateral(d, {'b': 1}, 5), unilateral(d, {'b': .25, 'c': .75}, 5))
        self.assertEqual(unilateral(d, {'a': .2, 'b': .8}, 5), (.8, 'a'))
        self.assertEqual(unilateral(d, {'b': 1}, 2), (.4, 'a'))

    def test_unknown_units_are_neutral(self):
        d, n = dist({'x': {'a'}, 'y': {'a'}, 'z': set()})
        known, k = dist({'x': {'a'}, 'y': {'a'}})
        self.assertEqual(unilateral(d, {'b': 1}, n), unilateral(known, {'b': 1}, k))

    def test_age_uses_attested_members_and_keeps_missing_dates(self):
        heads = {
            '1': {'Language_ID':'Indo-Aryan','Form':'*a','Tags':'Early-Vedic'},
            '1-2': {'Language_ID':'Indo-Aryan','Form':'b','Tags':'Epic Classical'},
            '2': {'Language_ID':'Indo-Aryan','Form':'c','Tags':''},
        }
        self.assertEqual(age('1','head',heads,{}), 'Reconstructed only')
        self.assertEqual(age('1','entry',heads,{'1-2':'1'}), 'Epic')
        self.assertEqual(age('2','entry',heads,{}), 'Undated OIA')


if __name__ == '__main__':
    unittest.main()
