# Chapter 10: APM (Asynchronous Programming Model) (Legacy)

## Core Idea
The Asynchronous Programming Model (APM) was the original way .NET handled asynchronous I/O, using `IAsyncResult` and `BeginFoo`/`EndFoo` method pairs.

## Key Concepts
- **IAsyncResult**: An interface representing the status of an asynchronous operation.
- **Callback Hell**: Because `BeginFoo` requires passing an `AsyncCallback` delegate, chaining multiple I/O operations results in deeply nested and hard-to-read code.

## Key Takeaways
1. APM is entirely superseded by `async/await`.
2. You can wrap legacy APM methods into Tasks using `TaskFactory.FromAsync`.\n