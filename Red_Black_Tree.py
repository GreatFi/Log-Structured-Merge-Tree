"""

This program implements a Red black tree in python which acts the memtable for the lsm tree algorithm where data is stored for faster writes to the database.

"""

import sys
from write_ahead_log import WAL
import os
MAX_BYTES_SIZE = 1024 * 1024

class Node:
    
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.color = "RED"
        self.left = None
        self.right = None
        self.parent = None

class RedBlackTree:

    def __init__(self, wal_filename, sstable_filename=None):
        self.wal = WAL.instance(wal_filename)
        self.NIL = Node(0)
        self.NIL.color = "BLACK"
        self.root = self.NIL
        self.current_size = 0
        self.sstable_filename = sstable_filename
        self.wal_filename = wal_filename

        rows = self.wal.replay(wal_filename)

        for row in rows:
            self.insert_key(row[1], row[2])

    def insert_key(self, key, value):
        node = Node(key, value)

        node.right = self.NIL
        node.left = self.NIL

        self.wal.write(f"PUT,{node.key},{node.value}\n")

        if self.root is self.NIL:
            self.root = node     
            node.color = "BLACK"
        else:
            current = self.root
            parent = None
            while current is not self.NIL:
                if node.key < current.key:
                    parent = current
                    current = current.left 
                else:
                    parent = current
                    current = current.right 
            node.parent = parent

            if node.key < parent.key:
                parent.left = node
            else:
                parent.right = node
            self.try_rebalance(node)

        node_length = sys.getsizeof(node.key) + sys.getsizeof(node.value)
        self.current_size += node_length

        if self.current_size >= MAX_BYTES_SIZE:
            self.flush()

    
    def in_order_traversal(self, node, result_list = []):
        
        if node != self.NIL:
            self.in_order_traversal(node.left, result_list)
            result_list.append((node.key, node.value))
            self.in_order_traversal(node.right, result_list)

        return result_list


    def flush(self):
        entries = self.in_order_traversal(self.root)
        with open(self.sstable_filename, mode="w") as f:
            
            for key, value in entries:
                f.write(f"{key},{value}\n")

        os.remove(self.wal_filename)

        self.root = self.NIL
        self.current_size = 0

    def try_rebalance(self, node):
        
        if self.root is node:
            node.color = "BLACK"
            return
        
        if node.parent.color == "BLACK":
            return
        
        if node.parent == node.parent.parent.right:
            uncle = node.parent.parent.left  
        else:
            uncle = node.parent.parent.right

        if uncle is not None and uncle.color == "RED":

            uncle.color = "BLACK"
            grand_parent = node.parent.parent
            node.parent.color = "BLACK"
            grand_parent.color= "RED"
            self.try_rebalance(grand_parent)
        elif uncle is self.NIL or uncle.color == "BLACK":
            self.fix_insert(node)
        
        
    def left_rotate(self, node):
        y = node.right
        node.right = y.left

        if y.left is not self.NIL:
            y.left.parent = node
        y.parent = node.parent

        if node.parent is self.NIL:
            self.root = y
        elif node == node.parent.left:
            node.parent.left = y
        else:
            node.parent.right = y
        y.left = node
        node.parent = y
    
    def right_rotate(self, node):
        y = node.left
        node.left = y.right

        if y.right is not self.NIL:
            y.right.parent = node
        y.parent = node.parent

        if node.parent is self.NIL:
            self.root = y
        elif node == node.parent.right:
            node.parent.right = y
        else:
            node.parent.left = y
        y.right = node
        node.parent = y

    def fix_insert(self, node):
        grand_parent = node.parent.parent
        parent = node.parent
        if node.parent == node.parent.parent.left:
            uncle = node.parent.parent.right
            if uncle.color == "BLACK" and node == node.parent.right:
                self.left_rotate(parent)
                self.right_rotate(grand_parent)
                node.color = "BLACK"
                grand_parent.color = "RED"
            elif uncle.color == "BLACK" and node == node.parent.left:
                self.right_rotate(grand_parent)
                parent.color = "BLACK"
                grand_parent.color = "RED"
        else:
            uncle = node.parent.parent.left
            if uncle.color == "BLACK" and node == node.parent.left:
                self.right_rotate(parent)
                self.left_rotate(grand_parent)
                node.color = "BLACK"
                grand_parent.color = "RED"
            elif uncle.color == "BLACK" and node == node.parent.right:
                self.left_rotate(grand_parent)
                parent.color = "BLACK"
                grand_parent.color = "RED"
    
    def search(self, key):
        
        current = self.root
        while current is not self.NIL:
            if key == current.key:
                return current.value
            elif key < current.key:
                current = current.left
            else:
                current = current.right
        return False
        
    def delete(self, key):
        self.insert_key(key, "tombstone")

