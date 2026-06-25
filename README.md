LSM TREE - Overview
---------------------------------
This repository implements the Log-Structured-Merged Tree algorithm used for handling write heavy systems like blockchain crypto currency storages, logging systems and many more.This algorithm also powers alot of key-value stores like LevelDB and RocksDB.It comprises of different components or rather data structures that help in data transition from memory to disk, you might be wondering why data should go from memory to disk,well...in this system we accept writes to memory first because it's faster, I/O operations on memory are usually very fast but data on there aren't persistent which means data gets lost when the system goes down,that's where the disk comes in,too much I/O operations on disk can get expensive both data related and financially because of the hardware costs, deprecation and so on but data stored there persists even if there is an outage or the system crashes.

Here is the write path:

Write Ahead Log
      |
Memtable(RedBlackTree)
      | 
Flushes to the sstables on disk
      |
Then those sstables are compacted to reduce disk space consumption

This is a summarised diagram of the lifecycle of the data being written to the lsm tree.

Reading from the lsm tree is more like this:
Memtable
   | -> (Bloomfilters)
The sstables on Disk
You may be wondering why Bloom filters were added in between but i will talk about each file individually in more detail.

MAJOR OPERATIONS IN THIS IMPLEMENTATION:
-------------------------------------------------
- Writes
- Reads
- Deleting
- Flushing
- Compaction

COMPONENTS OF THE LSM TREE
-----------------------------

WRITE-AHEAD-LOG:

This is one of the most important components in this system, this component helps in recovery/reliability,most times processes can be interrupted with power outages, systems crashing unexpectedly but that is normal,faults and outages are bound to happen,so what this system encourages is adding a write ahead log,as the name implies the operations being executed are written to an append only file which is necessary here,why? this file format allows writes to it which is replayed after an outage to reconstruct the memtable back to it's original state before the crash.

MEMTABLE:

This is the in-memory data structure that accepts writes and stores them temporarily,as i stated earlier in the brief overiew,the memtable stays on memory because I/O operations are faster there which is basically the point of the lsm tree(accept writes super fast then save to disk later).
