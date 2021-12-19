import unittest
import analyse

class TestPopulateTable(unittest.TestCase):
    def test_empty(self):
        t = analyse.populate_table([[[]]], {}, [[[]]], [])
        self.assertEqual(t, [[[]]])

    def test_special_special_match(self):
        table = [[[0 for x in range(len(analyse.variants)*2)] for y in range(len(analyse.variants)*2)]]
        ioms = {'0*': 0, '0m': 1, '0a': 2, '0o': 3, '1*': 4, '1m': 5, '1a': 6, '1o': 7}
        exclusions = []
        t = analyse.populate_table(table, ioms, [[['0*','1*']]],exclusions)
        self.assertEqual(t[0][0], [1,0,0,0,1,0,0,0])
        self.assertEqual(t[0][1], [0,0,0,0,0,0,0,0])
        self.assertEqual(t[0][2], [0,0,0,0,0,0,0,0])
        self.assertEqual(t[0][3], [0,0,0,0,0,0,0,0])
        self.assertEqual(t[0][4], [0,0,0,0,1,0,0,0])
        self.assertEqual(t[0][5], [0,0,0,0,0,0,0,0])
        self.assertEqual(t[0][6], [0,0,0,0,0,0,0,0])
        self.assertEqual(t[0][7], [0,0,0,0,0,0,0,0])

    def test_special_normal_match(self):
        table = [[[0 for x in range(len(analyse.variants)*2)] for y in range(len(analyse.variants)*2)]]
        ioms = {'0*': 0, '0m': 1, '0a': 2, '0o': 3, '1*': 4, '1m': 5, '1a': 6, '1o': 7}
        exclusions = []
        t = analyse.populate_table(table, ioms, [[['0*','1']]], exclusions)
        self.assertEqual(t[0][0], [1,0,0,0,1,1,1,1])
        self.assertEqual(t[0][1], [0,0,0,0,0,0,0,0])
        self.assertEqual(t[0][2], [0,0,0,0,0,0,0,0])
        self.assertEqual(t[0][3], [0,0,0,0,0,0,0,0])
        self.assertEqual(t[0][4], [0,0,0,0,1,1,1,1])
        self.assertEqual(t[0][5], [0,0,0,0,0,1,1,1])
        self.assertEqual(t[0][6], [0,0,0,0,0,0,1,1])
        self.assertEqual(t[0][7], [0,0,0,0,0,0,0,1])

    def test_normal_special_match(self):
        table = [[[0 for x in range(len(analyse.variants)*2)] for y in range(len(analyse.variants)*2)]]
        ioms = {'0*': 0, '0m': 1, '0a': 2, '0o': 3, '1*': 4, '1m': 5, '1a': 6, '1o': 7}
        exclusions = []
        t = analyse.populate_table(table, ioms, [[['0','1*']]], exclusions)
        self.assertEqual(t[0][0], [1,1,1,1,1,0,0,0])
        self.assertEqual(t[0][1], [0,1,1,1,1,0,0,0])
        self.assertEqual(t[0][2], [0,0,1,1,1,0,0,0])
        self.assertEqual(t[0][3], [0,0,0,1,1,0,0,0])
        self.assertEqual(t[0][4], [0,0,0,0,1,0,0,0])
        self.assertEqual(t[0][5], [0,0,0,0,0,0,0,0])
        self.assertEqual(t[0][6], [0,0,0,0,0,0,0,0])
        self.assertEqual(t[0][7], [0,0,0,0,0,0,0,0])

    def test_normal_normal_match(self):
        table = [[[0 for x in range(len(analyse.variants)*2)] for y in range(len(analyse.variants)*2)]]
        ioms = {'0*': 0, '0m': 1, '0a': 2, '0o': 3, '1*': 4, '1m': 5, '1a': 6, '1o': 7}
        exclusions = []
        t = analyse.populate_table(table, ioms, [[['0','1']]], exclusions)
        self.assertEqual(t[0][0], [1,1,1,1,1,1,1,1])
        self.assertEqual(t[0][1], [0,1,1,1,1,1,1,1])
        self.assertEqual(t[0][2], [0,0,1,1,1,1,1,1])
        self.assertEqual(t[0][3], [0,0,0,1,1,1,1,1])
        self.assertEqual(t[0][4], [0,0,0,0,1,1,1,1])
        self.assertEqual(t[0][5], [0,0,0,0,0,1,1,1])
        self.assertEqual(t[0][6], [0,0,0,0,0,0,1,1])
        self.assertEqual(t[0][7], [0,0,0,0,0,0,0,1])

    def test_normal_normal_excl_match(self):
        table = [[[0 for x in range(len(analyse.variants)*3)] for y in range(len(analyse.variants)*3)]]
        ioms = {'0*': 0, '0m': 1, '0a': 2, '0o': 3, '1*': 4, '1m': 5, '1a': 6, '1o': 7, '2*': 8, '2m': 9, '2a': 10, '2o': 11}
        exclusions = ['2']
        t = analyse.populate_table(table, ioms, [[['0','1','2o'], ['2a']]], exclusions)
        self.assertEqual(t[0][0], [1,1,1,1,1,1,1,1,0,0,0,0])
        self.assertEqual(t[0][1], [0,1,1,1,1,1,1,1,0,0,0,0])
        self.assertEqual(t[0][2], [0,0,1,1,1,1,1,1,0,0,0,0])
        self.assertEqual(t[0][3], [0,0,0,1,1,1,1,1,0,0,0,0])
        self.assertEqual(t[0][4], [0,0,0,0,1,1,1,1,0,0,0,0])
        self.assertEqual(t[0][5], [0,0,0,0,0,1,1,1,0,0,0,0])
        self.assertEqual(t[0][6], [0,0,0,0,0,0,1,1,0,0,0,0])
        self.assertEqual(t[0][7], [0,0,0,0,0,0,0,1,0,0,0,0])
        self.assertEqual(t[0][8], [0,0,0,0,0,0,0,0,0,0,0,0])
        self.assertEqual(t[0][9], [0,0,0,0,0,0,0,0,0,0,0,0])
        self.assertEqual(t[0][10], [0,0,0,0,0,0,0,0,0,0,0,0])
        self.assertEqual(t[0][11], [0,0,0,0,0,0,0,0,0,0,0,0])


if __name__ == '__main__':
    unittest.main()