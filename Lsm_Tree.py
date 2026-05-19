"""
This file is the main orchestrator for the lsm tree algo implementation.This ties every other file together.
"""

from Red_Black_Tree import RedBlackTree
from write_ahead_log import WAL


class LSMTREE:

    def __init__(self, wal_filename, sstable_filename):
        self.memtable = RedBlackTree(wal_filename, sstable_filename)
        self.WAL = WAL.instance(wal_filename)
        self.levels = []
        
        