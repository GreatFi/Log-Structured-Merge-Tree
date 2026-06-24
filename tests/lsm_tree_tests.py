"""
Test suite for the LSM Tree implementation in src/Lsm_Tree.py
"""

import unittest
from unittest.mock import patch
import src.Lsm_Tree as lsm_tree
from src.Lsm_Tree import LSMTREE, MAX_BYTES_SIZE
import glob
import os
from src.Red_Black_Tree import RedBlackTree
import threading
import time
class TestLSMTree(unittest.TestCase):

    def tearDown(self):
        
        sstables = glob.glob("sstable*")
        lsm_tree.MAX_LEVEL_SIZE = 5
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

        wal_recovery =self.lsm.active_WAL.replay("wal_1")
        memtable_key = self.lsm.active_memtable.search("key1")

        self.assertEqual(memtable_key, "value1")
        self.assertEqual([['PUT', 'key1', 'value1'], ['PUT', 'key2', 'value2'], ['PUT', 'key3', 'value3']], wal_recovery)

    def test_delete(self):
        self.lsm = LSMTREE("wal_1", "sstable")

        self.lsm.write("key4", "value4")
        self.lsm.delete("key4")

        memtable_search = self.lsm.active_memtable.search("key4")
        print(memtable_search)
        # asserted with isNone because of the search condition - tomstone values return none
        self.assertIsNone(memtable_search)

    def test_read(self):
        self.lsm = LSMTREE("wal_1", "sstable")
        self.lsm.write("key5", "value5")
        result = self.lsm.read("key5")
        self.assertEqual(result, "value5")

    def test_read_invalid_key(self):
        self.lsm = LSMTREE("wal_1", "sstable")
        # key doesn't exist
        read_key = self.lsm.read("key1")
        self.assertIsNone(read_key)

    def test_flush(self):
        self.lsm = LSMTREE("wal_1", "sstable")
        self.lsm.current_size = MAX_BYTES_SIZE - 1

        self.lsm.write("key7", "value7")
        result = self.lsm.read("key7")
        self.assertEqual(result, "value7")

    def test_compaction(self):
        self.lsm = LSMTREE("wal_1", "sstable")

        self.lsm.write("key8", "value8")
        self.lsm.write("key9", "value9")
        self.lsm.write("key10", "value10")
        self.lsm.flush()

        self.lsm.write("key11", "value11")
        self.lsm.write("key12", "value12")
        self.lsm.write("key13", "value13")
        self.lsm.flush()

        self.lsm.write("key14", "value14")
        self.lsm.write("key15", "value15")
        self.lsm.write("key16", "value16")
        self.lsm.flush()

        self.lsm.write("key17", "value17")
        self.lsm.write("key18", "value18")
        self.lsm.write("key19", "value19")
        self.lsm.flush()
        print(self.lsm.levels)
        ans = self.lsm.read("key8")

        self.assertEqual(self.lsm.levels[0], [])
        self.assertEqual(self.lsm.levels[1], ["sstable4"])
        self.assertEqual(ans, "value8")

    # test to check if compaction will work without hitting the threshold
    def test_compaction_no_op(self):
        self.lsm = LSMTREE("wal_1", "sstable")

        self.lsm.write("key20", "value20")
        self.lsm.write("key21", "value21")

        self.lsm.flush()
        print(self.lsm.levels)
        self.assertEqual(self.lsm.levels[0], ['sstable0'])

    def test_tombstone_compaction(self):
        self.lsm = LSMTREE("wal_1", "sstable")
        lsm_tree.MAX_LEVEL_SIZE = 1
        lsm_tree.LSMTREE
        self.lsm.write("key23", "value23")
        self.lsm.delete("key23")
        self.lsm.flush()

        self.lsm.write("key24", "value24")
        self.lsm.flush()

        self.lsm.write("key25", "value25")
        self.lsm.flush()

        self.lsm.write("key26", "value26")
        self.lsm.flush()

        result =self.lsm.read("key23")
        result2 =self.lsm.read("key24")
        self.assertIsNone(result)
        self.assertEqual(result2, "value24")
        
    def test_thread_safety(self):
        self.lsm = LSMTREE("wal_1", "sstable")

        t1 = threading.Thread(target=self.lsm.write, args=("key25", "value25"))
        t2 = threading.Thread(target=self.lsm.write, args=("key26", "value26"))

        t1.start()
        t2.start()
        t1.join()
        t2.join()

        thread_result_1 =self.lsm.read("key25")
        thread_result_2 =self.lsm.read("key26")

        self.assertEqual(thread_result_1, "value25")
        self.assertEqual(thread_result_2, "value26")

    def test_double_buffering(self):
        self.lsm = LSMTREE("wal_1", "sstable")
        real_transversal = RedBlackTree.in_order_traversal
        event = threading.Event()

        def fake_transversal(self, root, result_list=None):
            if result_list is None:
                event.set()
                time.sleep(0.1)
            return real_transversal(self, root, result_list)
        # writes here cause the flush method to be called, which will trigger the fake_transversal method which won't work if there are no inserts
        self.lsm.write("key17", "value17")
        self.lsm.write("key18", "value18")
        self.lsm.write("key19", "value19")
        self.lsm.write("key20", "value20")

        with patch.object(RedBlackTree, 'in_order_traversal', fake_transversal):
            main_thread = threading.Thread(target=self.lsm.flush)
            main_thread.start()

            event.wait()
            self.lsm.write("key1", "value1")
            self.lsm.write("key2", "value2")
            self.lsm.write("key3", "value3")
            self.lsm.write("key4", "value4")

            main_thread.join()
            value = self.lsm.memtable_2.search("key1")
            print(value)
            self.assertEqual(self.lsm.memtable_2.search("key1"), "value1")
