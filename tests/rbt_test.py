"""
Test suite for the red black tree implementation in src/Red_Black_Tree.py
"""
import unittest 
from src.Red_Black_Tree import RedBlackTree, BLACK, RED

class TestRedBlackTree(unittest.TestCase):
    
    def test_root_color(self):
        rbt = RedBlackTree()

        rbt.insert_key(10, "value1")
        self.assertEqual(rbt.root.color, BLACK)

    def test_insert(self):
        rbt = RedBlackTree()

        rbt.insert_key(10, "value2")
        rbt.insert_key(8, "value3")
        self.assertEqual(rbt.root.left.key, 8)
        self.assertEqual(rbt.root.left.color, RED)

    def test_left_rotate(self):
        rbt = RedBlackTree()

        rbt.insert_key(1, "value1")
        rbt.insert_key(2, "value1")
        rbt.insert_key(3, "value1")
        self.assertEqual(rbt.root.key, 2)
        self.assertEqual(rbt.root.color, BLACK)

        '''
        diagram representing the left rotation

             1                   2
               \        ->      /  \
                2              1    3
                 \
                  3
        '''


    def test_right_rotate(self):
        rbt = RedBlackTree()

        rbt.insert_key(11, "value11")
        rbt.insert_key(10, "value10")
        rbt.insert_key(9, "value9")
        self.assertEqual(rbt.root.key, 10)
        self.assertEqual(rbt.root.color, BLACK)
        self.assertEqual(rbt.root.left.color, RED)
        self.assertEqual(rbt.root.right.color, RED)

        """
         diagram representing the right rotation

            11              10
            /      ->      /  \
           10             9    11
          /                  
         9        
        """


    def test_fix_insert(self):
        rbt = RedBlackTree()

        rbt.insert_key(20, "value20")
        rbt.insert_key(22, "value20")
        rbt.insert_key(21, "value20")
        self.assertEqual(rbt.root.key, 21)

        """
        diagram of the zig zag scenario which the fix_insert method handles 
            20                               20                                              21
              \                                \                                            /  \
              22         ->                    21                 ->                      20   22
             /    (right rotation on 22)         \         (left rotation on 20)
            21                                   22
        """

    def test_search(self):
        rbt = RedBlackTree()

        rbt.insert_key(5, "value1")
        rbt.insert_key(2, "value2")
        rbt.insert_key(6, "value6")
        rbt.insert_key(4, "tombstone")

        # search for key that has a tombstone value
        key_1 = rbt.search(4)

        # search for key that exists
        key_2 = rbt.search(5)

        # search for key that doesn't exist
        key_3 = rbt.search(3)
        
        self.assertIsNone(key_1)
        self.assertEqual(key_2, "value1")
        self.assertFalse(key_3)

    def test_in_order_trasversal(self):
        rbt = RedBlackTree()

        # case when there are no nodes inserted
        results = rbt.in_order_traversal(rbt.root)

        # returns an empty list
        print(results)
        self.assertListEqual([], results)

        # case when nodes are inserted
        rbt.insert_key(20, "value20")
        rbt.insert_key(19, "value19")
        rbt.insert_key(18, "value18")
        rbt.insert_key(21, "value21")
        rbt.insert_key(22, "value22")

        more_results = rbt.in_order_traversal(rbt.root)
        self.assertEqual([(18, 'value18'), (19, 'value19'), (20, 'value20'), (21, 'value21'), (22, 'value22')], more_results)
        print(more_results)
        

