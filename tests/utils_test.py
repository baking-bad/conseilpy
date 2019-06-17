import unittest
from parameterized import parameterized
from loguru import logger

from conseilpy.utils import prepare_name


class Test_Utils(unittest.TestCase):
    @parameterized.expand([
        ("tezos", "tezos"),
        ("tezos name", "tezosname"),
        ("tezos name data", "tezosnamedata"),
        (None, None),
    ])
    def test_prepare_name(self, name, expected):
        if expected is not None:
            self.assertEqual(prepare_name(name), expected)
        else:
            with self.assertRaises(ValueError):
                prepare_name(name)


if __name__ == '__main__':
    unittest.main()
