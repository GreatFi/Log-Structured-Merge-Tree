LSM TREE - Overview
---------------------------------
This repository implements the Log-Structured-Merge Tree algorithm used for handling write-heavy systems like blockchain storage, logging systems, and many more. This algorithm also powers a lot of key-value stores like LevelDB and RocksDB. It comprises different components, or rather data structures, that help with data transition from memory to disk. You might be wondering why data should go from memory to disk. Well, this system accepts writes to memory first because it's faster. I/O operations on memory are usually very fast, but data there isn't persistent, which means data gets lost when the system goes down. That's where the disk comes in. Too many I/O operations on disk can get expensive, both in terms of data and financially, because of hardware costs, depreciation, and so on. However, data stored on disk persists even if there is an outage or the system crashes.

Here is the write path:

```
Write Ahead Log
      |
Memtable(RedBlackTree)
      | 
Flushes to the sstables on disk
      |
Then those sstables are compacted to reduce disk space consumption
```
This is a summarised diagram of the lifecycle of the data being written to the lsm tree.

Reading from the lsm tree is more like this:
```
Memtable
   | -> (Bloomfilters)
The sstables on Disk
```
You may be wondering why Bloom filters were added in between but I will talk about each file individually in more detail.

USAGE
-
Here is a basic usage example
```
from src.Lsm_Tree import LSMTREE

lsm = LSMTREE("wal_1","sstable")
lsm.write("key", "value")
lsm.read("key")
lsm.delete("key")
```

MAJOR OPERATIONS IN THIS IMPLEMENTATION:
-------------------------------------------------
- Writes
- Reads
- Deletes
- Flushes
- Compactions

COMPONENTS OF THE LSM TREE
-----------------------------

WRITE-AHEAD-LOG:

This is one of the most important components in the system. It ensures recovery and reliability during unexpected interruptions like power outages or crashes. Since faults are inevitable, the WAL writes all operations to an append-only file. This file can be replayed after an outage to reconstruct the memtable back to its original state.

MEMTABLE:

This is the in-memory data structure that accepts writes and stores them temporarily. As I stated earlier in the brief overview, the memtable stays in memory because I/O operations are faster there, which is basically the point of the LSM tree (accept writes super fast then save to disk later). Here I used the RedBlackTree as the data structure for the memtable because of its self-balancing features, which allows it to have O(log N) time complexity. When this memtable reaches or surpasses the size threshold, which is a megabyte by default,the LSM tree flushes out the keys and values to disk in sorted order using the in_order_traversal method in the RedBlackTree.

BLOOM FILTER:

The bloom filter which appears in the read path diagram earlier,is one of the key pieces for read operations in this system.
When you perform read operations, the LSM tree loops through each SSTable file saved on disk. Well, this wouldn't be an issue if the number of SSTables were very little, but as the number of SSTables grow,looping through all those SSTables blindly looking for the key that might not even be in the SSTable gets really expensive.That's where the bloom filter comes in.This determines if the key being searched for is definitely not in that sstable(true negative) which allows the system to skip the sstable entirely saving us one pointless read operation on that sstable or might be in that sstable(false positive).

The parameters used to initialise the Bloom FIlter:
- num_inserts
- false_positive_prob
- existing_bitarray=None
  
The num_inserts(number of inserts) parameter represents the expected load of the system.
The false_positive_prob sets the desired probability of generating a false positive.
The existing bitarray param is exclusive for this implementation,but the first two applies everywhere for bloom filter implementations.

SSTABLES:

Sorted-String Tables also known as SSTables are files that hold the flushed key-value pairs from the memtable.The inorder traversal method in the memtable makes sure that all data flushed to the sstables must be sorted in ascending order.Sorted string table files enable efficient merging and compaction.It sets the foundation for index-based reads as a future improvement to the system.

LSM TREE - ORCHESTRATOR:

This component ties everything together. All operations in this system are carried out by this component be it writes,reads and the rest.

WRITES:

When the system starts off from an outage or a crash, it checks if the wal file exists on disk.It replays the wal to rebuild the memtable back to its original state. But if it starts off fresh,it just creates instances of both the memtable and the WAL, but not the bloom filter. The bloom filter instance is initialised later on in the flush method. So after startup,incoming writes are written to the memtable until the memtable hits the size threshold,then triggers the flushing of the data to disk.

READS:

For read operations, this component handles the full lifecycle of the read. It starts by searching the memtable for the key.If it's there, it returns the value immediately. If it isn't, it moves to disk, where the bloom filter comes in and works as described in the bloom filter section. Once the file holding the key is found, the value is returned.If the key isn't found at all, it returns None.

DELETES:

Deletes are straight forward,delete operations on a key replace that key's value with a tombstone value.This approach is used because deleting from memtables(if the key is on the memtable) can get ugly quickly.If the node has children,removing it means that we have to reassign its children to another parent which is too complicated.That's why I went with the earlier approach,most implementations handle deletes that way.

CONCURRENCY & FLUSH 
-
The double buffer pattern implemented here uses two WAL instances coupled to two memtable instances,where one pair is assigned as the active WAL and active memtable. This allows writes to be saved even when a flush is ongoing. In the flush method of the orchestrator,the active memtable is switched to the memtable that's not being flushed. You might notice that the flush method fails the single responsibility rule here, but I needed everything to run as atomically as possible.Improvements are to be made. The initialisation of the bloom filter happens once the swap has happened. Keys from the memtable are hashed and added to the bloom filter, then written to the SSTable accordingly.

COMPACTION
-

This is also a part of the lsm tree orchestrator

LevelDB inspired some of the design choices here.In this implementation, there are several levels on disk that hold the SSTables created during a flush. Once a level has reached or surpassed the threshold set, it automatically merges all the SSTables on that level and appends them to the next level, with the keys added to the bloom filter. This saves unnecessary disk I/O during reads.There are a total of five levels, levels 0 through 4, and each can hold a total of four SSTables. All flushes from memory land in the first level, level_0. Since this is the level where keys tend to be duplicated, during compaction only the most recent key is kept and others are discarded to improve storage efficiency.When keys with tombstone values are compacted all the way to the last level, level_4, the key is deleted permanently.

TESTS
-
Using the built in unittest python testing framework,I was able to carry out extensive tests that covers the memtable,wal,bloom filter and the LSMTREE orchestrator.
The tests on the memtable covers:
- Inserts.
- in_order_traversals.
- Search.
- Rebalancing(left and right rotations,zig-zag scenarios with fix_insert).
- Tombstone inserts or rather deletes.

The tests on the WAL covers:
- Ensuring the data appended to the file is saved to disk.
- The replay logic.

The tests on the Bloom Filter covers:
- The hashing of added keys.
- The check,to see if said added keys were hashed properly
- The formula for getting bitarray size and getting the number of hash functions

The tests on the LSMTREE orchestrator covers:
- Rebuilding the memtable from the WAL replay.
- The writes to the memtable.
- The reads from both the memtable and the sstable on disk.
- The tombstone updates when keys are deleted.
- The flush mechanism.
- The double buffer architecture
- The Compaction of sstables on disk
  
REQUIREMENTS
-
You will need python 3 to run this code.
Look into the requirements.txt file to see the dependencies I installed in my environment for this project.Then run:
```
pip install -r requirements.txt
```
to install them

HOW TO RUN THE TESTS:
-

In the home directory run these commands:

```
python -m unittest tests/rbt_test.py -v
python -m unittest tests/write_ahead_log_tests.py -v
python -m unittest tests/bloom_filter_tests.py -v    
python -m unittest tests/lsm_tree_tests.py -v
```
