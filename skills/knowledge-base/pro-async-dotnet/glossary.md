# Glossary

**AggregateException** — A wrapper exception used by the TPL to package one or more exceptions thrown by Tasks, particularly when multiple tasks are awaited simultaneously (e.g., Task.WhenAll). (Ch 4)
**Asynchronous** — A programming paradigm where an operation begins but execution control returns to the caller immediately, allowing the thread to do other work while waiting for completion. (Ch 1)
**CancellationToken** — A lightweight struct passed into asynchronous methods that they periodically check to cooperatively cancel operations. (Ch 4)
**Concurrency** — Dealing with multiple operations progressing at the same time, usually by interleaving execution on a single thread or yielding during waits. (Ch 1)
**Parallelism** — Executing multiple operations at the exact same physical time using multiple CPU cores. (Ch 1)
**PLINQ** — Parallel LINQ; an implementation of LINQ to Objects that executes queries concurrently across multiple cores. (Ch 8)
**SemaphoreSlim** — A lightweight synchronization primitive that limits the number of threads that can concurrently access a resource, and supports asynchronous waiting via WaitAsync. (Ch 7)
**SynchronizationContext** — A .NET abstraction representing the target environment or thread context (e.g., the UI thread) where code should execute. (Ch 5)
**Task** — An object representing the future completion of an asynchronous operation, which can optionally return a result. (Ch 2)
**ThreadPool** — A managed pool of background threads maintained by the .NET runtime to execute work items efficiently without the overhead of creating new OS threads. (Ch 2)\n