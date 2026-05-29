"""
This file is the main orchestrator for the lsm tree algo implementation.This ties every other file together.
"""

import os
import sys
from Red_Black_Tree import RedBlackTree
from write_ahead_log import WAL
MAX_BYTES_SIZE = 1024 * 1024
MAX_LEVEL_SIZE = 5
MAX_SSTABLES_PER_LEVEL = 4
class LSMTREE:

    def __init__(self, wal_filename, sstable_filename):

        self.memtable = RedBlackTree()
        self.WAL = WAL.instance(wal_filename)
        self.wal_filename = wal_filename
        self.current_size = 0
        self.sstable_filename = sstable_filename
        self.sstable_counter = 0
        self.sstable_base = "sstable"
        self.levels = [[]]

        if os.path.isfile(self.wal_filename):
            rows = self.WAL.replay(self.wal_filename)

            for row in rows:
                if row[0] == "PUT":
                    self.write(row[1], row[2])
                else:
                    self.delete(row[1])

    def write(self, key, value):

        self.WAL.write(f"PUT,{key},{value}\n")
        self.memtable.insert_key(key, value)
        self.current_size += sys.getsizeof(key) + sys.getsizeof(value)

        if self.current_size >= MAX_BYTES_SIZE:
            self.flush()

    def delete(self, key):
        self.WAL.write(f"DELETE,{key}\n")
        self.memtable.insert_key(key, "tombstone")
        
    def flush(self):
        entries = self.memtable.in_order_traversal(self.memtable.root)

        self.sstable_filename = f"{self.sstable_base}{self.sstable_counter}" 
        with open(self.sstable_filename, mode="w") as f:
            
            for key, value in entries:
                f.write(f"{key},{value}\n")
        self.sstable_counter += 1

        self.levels[0].append(self.sstable_filename)

                
        self.memtable.root = self.memtable.NIL
        self.current_size = 0

        os.remove(self.wal_filename)
        self.compaction()


        
    def read(self, key):

        result =self.memtable.search(key)
        if result:
            return result
        
        for level in self.levels:
            for level_0 in level:
                with open(level_0, mode="r") as file: 
                    line = file.readline()
                    while line:
                        key_value = line.split(",")
                        if key == key_value[0]:
                            return f"{key},{key_value[1]}"
                        line = file.readline()
        return None
         
    def compaction(self, level_number):
        
        level = self.levels[level_number]
        if len(level) >= MAX_SSTABLES_PER_LEVEL:

            new_level = []
            kv_dict = {}
            
            self.sstable_filename = f"{self.sstable_base}{self.sstable_counter}" 

            for sstables in level:
                with open(sstables, mode="r") as f:
                    for line in f:
                        kv = line.split(",")
                        if len(kv) < 2:
                            continue
                        if level_number == MAX_LEVEL_SIZE - 1 and kv[1].strip() == "tombstone":
                            continue
                        else:
                            kv_dict[kv[0]] = kv[1].strip()
                        
            with open(self.sstable_filename, mode="w") as f:
                for key, value in kv_dict.items():
                    f.write(f"{key},{value}\n")
            self.sstable_counter += 1 

            level_number += 1
            if len(self.levels) == level_number:
                new_level.append(self.sstable_filename)
                self.levels.append(new_level)
            else:
                self.levels[level_number].append(self.sstable_filename) 
 
            for sstables in level:
                os.remove(sstables)
            level.clear()

            self.compaction(level_number)

    