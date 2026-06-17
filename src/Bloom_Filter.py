"""
This file containes the implementation of the bloom filter, which is used to improve the read performance of the LSM TREE algorithm.
"""
from bitarray import bitarray
from math import log
from mmh3 import hash

class BloomFilter:

    def __init__(self, num_inserts, false_positive_prob, existing_bitarray = None):

        if num_inserts <= 0:
            raise ValueError("Inserts must be greater than zero")

        self.false_positive_prob = false_positive_prob
        self.bitarray_size = BloomFilter.get_bitarray_size(num_inserts, false_positive_prob)
        self.num_hash_func = BloomFilter.get_hash_func_count(self.bitarray_size, num_inserts)

        if existing_bitarray is not None:
            self.bitarray = existing_bitarray
        else:
            self.bitarray = bitarray(self.bitarray_size) 


    def addKey(self, insert:str):
        hash_values = []

        for seed in range(self.num_hash_func):
            hash_value = hash(insert, seed) % self.bitarray_size
            hash_values.append(hash_value)

            self.bitarray[hash_value] = True

    def check(self, insert):
        for seed in range(self.num_hash_func):
            hash_value = hash(insert, seed) % self.bitarray_size
            if self.bitarray[hash_value] == False:
                return False
        return True

    @staticmethod
    def get_bitarray_size(n, p):
        
        m = -(n * log(p)) / log(2)**2
        return int(m)
    
    @staticmethod
    def get_hash_func_count(m, n):
        
        k = (m/n) * log(2)
        return int(k)
    
