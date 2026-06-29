TRADEOFFS
-
Here are the design decisions I made and why I made them.

Architecture
-

WAL:
In my Write-Ahead Log(wal) I used the append only mode over the read/write or normal file mode because append only is faster,since it writes to the end of the file unlike the normal file mode.I prioritised speed here because the wal needs to accept writes as fast as possible.

I used two wal instances instead of the singleton because of the double buffer architecture,which I was trying to achieve, and which isn't possible when the WAL can have only one instance.Although the singleton pattern ensures durability,Two wal instances are the foundation to the Multithreading.The complications like swapping between wal instances and so on wouldn't occur in the singleton pattern but it was a necessary tradeoff to achieve concurrency.

MEMTABLE:
I chose the RedBlack Tree as my memtable over other options like the skip list because of its self balancing feature,O(Log N) time complexity guaranteed during reads and the sorted output during traversals.I got cleaner sorted traversal from the RedBlack Tree over the easier concurrency with the skip list.

I used tombstone deletes over in-place deletes here because the complications in-place deletes introduce like reattaching children if the node deleted was a parent,recolouring and so on,wasn't something worth dealing with in this implementation. 

BLOOM FILTER:
In my BloomFilter,I decided to use the MurmurHash3 with seeds over independent hash functions because creating k hash functions and running keys through each of them gives room for errors.Configuring multiple hash functions can get really tricky.That's why I went with creating one hash function and running it k times.It's faster and gives less room for errors.Although the mapping of bits in the bitarray may not be that efficient it was still a better option.

When creating the bloom filter file,I needed to write both the number of keys and bitarray bytes simultaneously which isn't possible with the normal file write method.I decided to use pickle to write both information to the bloom filter file.Pickling files in python is exclusive to python,I could've opted to use JSON but it doesn't handle binary format data very well.

CONCURRENCY
-

WRITE LOCK:
In my write method I added a thread lock holding the insert,size update,and flush.This was a coarse grained lock.During tests,the data written after the swap has happened was not corrupted.The issue with that approach arose when a write triggers a flush,which triggers a compaction without releasing the lock,causing incoming writes to wait.I decided to remove the flush from the lock in the write method and added a lock to the swap in the flush method,allowing the flush to continue even when the lock is released.The next hurdle was the double flush race condition which can be handled by adding a flag to indicate that a flush is ongoing.The coarse grained lock was less complicated but had significant impact on the performance of the system which is what I am prioritising here.

COMPACTION:
Compaction in this implementation is synchronous.The write thread that triggered the flush, which in turn triggered compaction, is occupied until the heavy I/O to disk is complete, which impacts performance.I considered running compaction on a separate thread,but the complications arising from handling shared resources and concurrent reads could lead to data corruption, which is not acceptable here.I chose data integrity over performance.

TESTS
-
While working with WAL files during tests,I realised that deleting the WAL after the memtable it was coupled to had been flushed meant that swapping back to it later would fail, since it no longer exists at that memory address. That's why I decided to truncate the file to 0 bytes instead, allowing easy swapping.

Trying to perform operations on a file that has its stream open will throw errors.I hit that error when trying to truncate the WAL file,which is why I decided to close file streams before carrying out any operation.

To simulate the double buffer during tests,I used threading.Event combined with time.sleep. Using time.sleep alone on the flush method wouldn't have accurately replicated the scenario I wanted to create.By combining threading.Event with time.sleep, I was able to slow down the in-order traversal,which is where the most work is done during a flush, giving concurrent writes enough time to come in during the flush.

To test whether tombstone values are dropped at the last level of compaction,I reduced the maximum number of levels from 5 to 1 instead of writing and flushing multiple times. Testing with the full configuration would require 4 SSTables across 5 levels, which is a large number of writes just for a single test.Reducing the maximum level size to 1 kept the test focused and fast.

Similarly, to test the size threshold that triggers a memtable flush, writing up to a full megabyte of data would be tedious. Reducing the maximum memtable size to one write below the flush threshold made the test straightforward to execute.
