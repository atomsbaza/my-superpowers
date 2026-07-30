# Chapter 8: PLINQ (Parallel LINQ)

## Core Idea
PLINQ extends standard LINQ to objects by automatically parallelizing the execution of queries across multiple CPU cores.

## Key Concepts
- **AsParallel()**: The extension method that converts an `IEnumerable` into a `ParallelQuery`, instructing the runtime to partition the data and process it in parallel.
- **AsOrdered()**: Forces PLINQ to preserve the original ordering of the data (which adds overhead).
- **ForAll**: A parallelized version of `foreach` that is highly efficient for PLINQ queries because it doesn't require merging the results back into a single thread.

## Mental Models
- Think of PLINQ as a **declarative parallel loop**. You tell the compiler *what* you want to process, and it figures out *how* to split the work across cores.

## Key Takeaways
1. PLINQ is excellent for data-parallel, CPU-bound operations.
2. Not every query is faster with PLINQ. Small datasets or complex ordering requirements can cause parallel overhead to outweigh the benefits.\n