"""
Test suite for the LSM Tree implementation in src/Lsm_Tree.py
"""

import unittest
from src.Lsm_Tree import LSMTREE
import glob
import os

class TestLSMTree(unittest.TestCase):

    def tearDown(self):
        
        sstables = glob.glob("sstable*")
        for sstable in sstables:
            os.remove(sstable)
        wals = glob.glob("wal_*")
        self.lsm.WAL_1.stream.close()
        self.lsm.WAL_2.stream.close()
        for wal in wals:
            os.remove(wal)

    def test_write(self):
        self.lsm = LSMTREE("wal_1", "sstable")

        self.lsm.write("key1", "value1")    
        self.lsm.write("key2", "value2")    
        self.lsm.write("key3", "value3")   

        recovery =self.lsm.active_WAL.replay("wal_1")
        memtable = self.lsm.active_memtable.search("key1")

        self.assertEqual(memtable, "value1")
        self.assertEqual([['PUT', 'key1', 'value1'], ['PUT', 'key2', 'value2'], ['PUT', 'key3', 'value3']], recovery)
