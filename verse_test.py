import unittest
import analyse

class TestGetDecorations(unittest.TestCase):
    def test_only_undecorated(self):
        v = analyse.Verse([1,1,1,1], [[['1','2']]],[], ['1','2'])
        self.assertEqual(v.decorations, {'1': {'*'},'2':{'*'}})

    def test_only_half_decorated(self): 
        v = analyse.Verse([1,1,1,1], [[['1a','2m']]], [], ['1','2'])
        self.assertEqual(v.decorations, {'1': {'a', 'o'},'2':{'*', 'm'}})
        v = analyse.Verse([1,1,1,1], [[['1o','2*']]], [], ['1','2'])
        self.assertEqual(v.decorations, {'1': {'a', 'o'},'2':{'*', 'm'}})

    def test_excluded(self):
        v = analyse.Verse([1,1,1,1], [[['1a','2m']]], ['2'], ['1','2'])
        self.assertEqual(v.decorations, {'1': {'a', 'o'}})

    def test_implied(self):
        v = analyse.Verse([1,1,1,1], [[['1']]],[], ['1','2'])
        self.assertEqual(v.decorations, {'1': {'*'},'2':{'*'}})            

    

if __name__ == '__main__':
    unittest.main()