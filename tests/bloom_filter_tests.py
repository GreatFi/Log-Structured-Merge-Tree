"""
Test suite for the bloom filter implementation in src/Bloom_Filter.py
"""
from math import log
import unittest
from src.Bloom_Filter import BloomFilter

class TestBloomFilter(unittest.TestCase):

    def test_addkey(self):
        bf = BloomFilter(60, 0.01)

        # use strings for addkeys
        bf.addKey("45")
        result = bf.check("45")
        result_2 = bf.check("47")
        self.assertFalse(result_2)
        self.assertEqual(result, True)

    def test_bitarray_size_formula(self):
        # m = -(n * log(p)) / log(2)**2
        
        m = BloomFilter.get_bitarray_size(100, 0.01)
        # m = -(100 * log(0.01)) / log(2)**2
        self.assertEqual(m, 958)
        # returns an int, that is why i removed the decimals and left it as the original whole number

    def test_hash_func_count_formula(self):
        # k = (m/n) * log(2)

        k = BloomFilter.get_hash_func_count(958, 100)
        # k = (958/100 * log(2))

        self.assertEqual(k,6)
        # same thing i described in the earlier test also applies here

        