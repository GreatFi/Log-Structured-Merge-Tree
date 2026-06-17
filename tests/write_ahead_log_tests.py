"""
Test suite for the write ahead log implementation in src/Write_Ahead_Log.py
"""

import unittest
import os
from src.write_ahead_log import WAL
FILE = "wal"

class TestWAL(unittest.TestCase):
    
    def tearDown(self):
        if os.path.isfile(FILE):
            self.wal.stream.close()
            os.remove(FILE)

    # this test checks if the file is saved to disk
    def test_write_to_disk(self):
        self.wal = WAL(FILE)

        self.wal.write("key1, value1\n")
        self.wal.write("key2, value2\n")
        self.wal.write("key3, value3\n")

        if os.path.isfile(FILE):
            with open(FILE, mode="r") as f:
                data =f.read()
            self.assertEqual("key1, value1\nkey2, value2\nkey3, value3\n", data)  

    def  test_replay(self):
        self.wal = WAL(FILE)

        self.wal.write("PUT,key1,value1\n")
        self.wal.write("PUT,key2,value2\n")
        self.wal.write("PUT,key3,value3\n")

        rows = self.wal.replay(FILE)
        print(rows)
        self.assertListEqual([['PUT','key1', 'value1'], ['PUT','key2', 'value2'], ['PUT','key3', 'value3']], rows)
        