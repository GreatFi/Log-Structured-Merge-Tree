"""
This file is the main orchestrator for the lsm tree algo implementation.This ties every other file together.
"""

import os
import threading
import sys
import pickle
from bitarray import bitarray
from src.Red_Black_Tree import RedBlackTree
from src.write_ahead_log import WAL
from src.Bloom_Filter import BloomFilter
MAX_BYTES_SIZE = 1024 * 1024
MAX_LEVEL_SIZE = 5
MAX_SSTABLES_PER_LEVEL = 4

class LSMTREE:

    def __init__(self, wal_filename, sstable_filename):

        self.memtable_1 = RedBlackTree()
        self.memtable_2 = RedBlackTree()
        self.WAL_1 = WAL("wal_1")
        self.WAL_2 = WAL("wal_2")
        self.active_WAL = self.WAL_1
        self.wal_filename = wal_filename
        self.current_size = 0
        self.sstable_filename = sstable_filename
        self.sstable_counter = 0
        self.sstable_base = "sstable"
        self.levels = [[]]
        self.active_memtable = self.memtable_1
        self.lock = threading.Lock()

        if os.path.isfile(self.wal_filename):
            rows = self.active_WAL.replay(self.wal_filename)

            for row in rows:
                if row[0] == "PUT":
                    self.write(row[1], row[2])
                else:
                    self.delete(row[1])

    def write(self, key, value:str):

        self.active_WAL.write(f"PUT,{key},{value}\n")
        value = value.strip("\n")
        
        
        with self.lock:
            self.active_memtable.insert_key(key, value)
            self.current_size += sys.getsizeof(key) + sys.getsizeof(value)

            if self.current_size >= MAX_BYTES_SIZE:
                self.flush()

    def delete(self, key):
        self.active_WAL.write(f"DELETE,{key}\n")
        with self.lock:
            self.active_memtable.insert_key(key, "tombstone")
        
    def flush(self):
    
        memtable_to_flush = self.active_memtable
        wal_to_truncate = self.active_WAL
        if self.active_memtable is self.memtable_1 and self.active_WAL is self.WAL_1:
            self.active_memtable = self.memtable_2
            self.active_WAL = self.WAL_2
        else:
            self.active_memtable = self.memtable_1
            self.active_WAL = self.WAL_1
        self.current_size = 0

        entries = memtable_to_flush.in_order_traversal(memtable_to_flush.root)
        self.sstable_filename = f"{self.sstable_base}{self.sstable_counter}" 

        bf = BloomFilter(memtable_to_flush.number_of_keys, 0.01)
        with open(self.sstable_filename, mode="w") as f:
            
            for key, value in entries:
                f.write(f"{key},{value}\n")
                bf.addKey(f"{key}") 
        inserts = bf.bitarray.tobytes()

        with open(f"{self.sstable_filename}_bloom", mode="wb") as bloom:
            pickle.dump({"n":memtable_to_flush.number_of_keys, "inserts":inserts}, bloom)
        
        self.sstable_counter += 1
        self.levels[0].append(self.sstable_filename)

                
        memtable_to_flush.root = memtable_to_flush.NIL
        memtable_to_flush.number_of_keys = 0

        os.truncate(wal_to_truncate.filename, 0)
        self.compaction(level_number=0)


        
    def read(self, key):
        
        result =self.active_memtable.search(key)
        if result:
            return result
        
        for level in self.levels:

            for level_0 in reversed(level):

                with open(f"{level_0}_bloom", mode="rb") as bloom:
                    result_dict = pickle.load(bloom)
                bit = bitarray()
                bit.frombytes(result_dict["inserts"])
                bf = BloomFilter(result_dict["n"],0.01, bit)
               
                if bf.check(key) is False:
                    continue
                with open(level_0, mode="r") as file: 
                    for line in file:
                        key_value = line.split(",")
                        if key == key_value[0]:
                            return f"{key_value[1].strip("\n")}"

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
            
            bf = BloomFilter(len(kv_dict), 0.01)
            with open(self.sstable_filename, mode="w") as f:
                for key, value in sorted(kv_dict.items()):
                    f.write(f"{key},{value}\n")
                    bf.addKey(f"{key}")
            inserts = bf.bitarray.tobytes()
            with open(f"{self.sstable_filename}_bloom", mode="wb") as bloom:
                pickle.dump({"n":len(kv_dict), "inserts":inserts}, bloom)

            self.sstable_counter += 1 

            level_number += 1
            if len(self.levels) == level_number:
                new_level.append(self.sstable_filename)
                self.levels.append(new_level)
            else:
                self.levels[level_number].append(self.sstable_filename) 
 
            for sstables in level:
                os.remove(sstables)
                os.remove(f"{sstables}_bloom")
            level.clear()

            self.compaction(level_number)

    