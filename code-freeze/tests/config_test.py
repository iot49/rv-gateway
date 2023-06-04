import unittest
from utilities import config

class TestConfig(unittest.TestCase):

    def test_set_get(self):
        config.set("testing", None)
        tests = [
            ("testing", None),
            ("testing", "types", "str:1:2;3", "abc: # 4243 $#%$^"),
            ("testing", "types", "int", -123),
            ("testing", "types", "flt", 3.1415),
            ("testing", "types", "dict", { 'a': 1, 'b': 2 }),
            ("testing", "deep", "a", "b", "c", "d", { 'a': 1, 'b': '2' }),
            ("testing", "x", "a", "b", "c", 5),
        ]
        for test in tests:
            config.set(*test)
            path = test[:-1]
            value = test[-1]
            with self.subTest(f"{path} = {value}"):
                self.assertEqual(config.get(*path), value)
        # set works only for only dicts
        config.set("testing", "deep", "a", "b", "c", 5)
        with self.assertRaises(AttributeError):
            config.set("testing", "deep", "a", "b", "c", 5, 123)
        # 0 or >1 parameters
        with self.assertRaises(ValueError):
            config.set("testing")
        # overwrite
        config.set("testing", "new value")
        self.assertEqual(config.get("testing"), "new value")
        self.assertTrue(config.modified())
        config.save()
        # verify that setting to idential value does not modify config
        self.assertFalse(config.modified())
        config.set("testing", "new value")
        self.assertFalse(config.modified())
         # remove tests from config
        config.set("testing", None)
        self.assertTrue(config.modified())
        config.save()
        self.assertFalse(config.modified())
 
if __name__ == '__main__':
    unittest.main()