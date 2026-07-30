# Chapter 10: Define Errors Out Of Existence

## Core Idea
Exception handling is one of the worst sources of complexity. The best way to deal with exceptions is to design your APIs so that the exceptional conditions simply do not exist in the first place.

## Frameworks Introduced
- **Define Errors Out of Existence**:
  - How: Change the semantics of a method so that a previously "exceptional" state is now just a normal part of the method's operation.
  - Example: `unset` in Tcl or `delete` in some maps. If you delete a key that doesn't exist, instead of throwing a `KeyNotFoundException`, just do nothing and return. The desired state (the key is not in the map) has been achieved.
- **Masking Exceptions**:
  - How: Handle the exception at a low level so the caller never sees it (e.g., TCP handling dropped packets by automatically retransmitting, rather than exposing the dropped packet to the application).

## Key Takeaways
1. Throwing an exception is passing the buck to the caller. If the caller doesn't know how to handle it either, the system becomes fragile.
2. Reduce the number of exceptions your modules throw.\n