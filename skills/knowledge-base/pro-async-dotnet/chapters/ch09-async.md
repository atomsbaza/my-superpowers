# Chapter 9: The BackgroundWorker and EAP (Legacy)

## Core Idea
Before the TPL and `async/await`, the Event-based Asynchronous Pattern (EAP) and `BackgroundWorker` were used primarily in UI applications to offload work to a background thread and marshal progress/completion events back to the UI thread.

## Key Concepts
- **BackgroundWorker**: A component that encapsulates a background thread, providing `DoWork`, `ProgressChanged`, and `RunWorkerCompleted` events.
- **EAP**: Methods ending in `Async` (e.g., `WebClient.DownloadStringAsync`) paired with a `Completed` event.

## Key Takeaways
1. These patterns are mostly obsolete for new development. Use `async/await` and `Task.Run` instead.
2. Understanding them is necessary for maintaining legacy WinForms/WPF applications.\n