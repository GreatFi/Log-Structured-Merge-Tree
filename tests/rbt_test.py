"""
Test suite for the red black tree implementation in src/Red_Black_Tree.py
"""
import unittest 
from src.Red_Black_Tree import RedBlackTree, Node, BLACK, RED


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
        diagram of the zig zag scenario/
            20                               20                                              21
              \                                \                                            /  \
              22         ->                    21                 ->                      20   22
             /    (right rotation on 22)         \         (left rotation on 20)
            21                                   22
        """

if __name__ == '__main__':
    unittest.main()
