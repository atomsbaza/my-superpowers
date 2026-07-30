# Chapter 6: Concurrent Collections

## Core Idea
Standard .NET collections (`List`, `Dictionary`) are not thread-safe. The `System.Collections.Concurrent` namespace provides specialized collections optimized for concurrent access.

## Key Concepts
- **ConcurrentDictionary**: Highly optimized for concurrent reads and writes, using fine-grained locking.
- **ConcurrentQueue / ConcurrentStack**: Lock-free, thread-safe FIFO and LIFO collections.
- **BlockingCollection**: A wrapper around `IProducerConsumerCollection` that blocks the thread if the collection is empty (when consuming) or full (when producing).

## Key Takeaways
1. Never use standard collections across multiple threads without explicit locking.
2. Use `BlockingCollection` to easily implement Producer-Consumer patterns.\n