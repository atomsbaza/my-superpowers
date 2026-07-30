# Software Design Cheatsheet

## The "Deep Module" Checklist

Before finishing a module, ask yourself:
1. **Does it hide a secret?** (Is there a design decision entirely encapsulated here?)
2. **Is the interface simpler than the implementation?** (Or am I just passing variables through?)
3. **If I explain how to use this, do I have to explain how it works internally?** (If yes, the abstraction has leaked).
4. **Is it somewhat general-purpose?** (Could someone else use this without caring about my specific feature?)

## Split or Combine?

| Condition | Action |
|---|---|
| Modules share detailed knowledge (e.g., a file format) | **Combine** to hide the knowledge in one place. |
| A method is just calling another method (pass-through) | **Combine** the layers. |
| The module is doing two completely unrelated things | **Split** to improve cohesion. |
| Splitting creates a highly general-purpose piece | **Split**, and use the general piece in the specific piece. |

## Exception Handling Heuristics

1. **Can I redefine the method so this isn't an error?** (e.g., `substring` returning an empty string instead of throwing if the index is out of bounds).
2. **Can I handle this exception internally?** (e.g., automatically reconnecting to a socket instead of throwing).
3. If neither, throw it. But strive to minimize these.

## The Rule of Comments

- **Don't**: Repeat the code (`// increments i`).
- **Do**: Explain *Why* (the reason for a decision, business logic rules).
- **Do**: Explain *What* at a high level (Interface comments).
- **Do**: Explain *Invariants* (Things that must remain true during execution).\n