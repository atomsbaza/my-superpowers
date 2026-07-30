# Chapter 32: GoF Case Study — Designing a Document Editor (Lexi)

## Core Idea
Lexi, a WYSIWYG document editor, is used to walk through seven concrete design problems end-to-end, showing that in every case the right move is to "encapsulate the concept that varies" in its own object — and that this single recurring move is what produces eight of the GoF patterns.

## Frameworks Introduced
- **Recursive composition (leading to Composite)**: build a document's physical structure by treating characters, graphics, and structural containers (rows, columns) all as instances of one abstract `Glyph` class, so simple and compound elements can be handled uniformly.
  - When to use: whenever a system needs to treat individual objects and arbitrarily-nested groups of objects the same way (draw, measure, hit-test) without the client caring which it has.
  - How: define an abstract class (`Glyph`) with `Draw`, `Intersects`, `Insert`, `Remove`, `Child` operations; give both leaf and composite subclasses compatible interfaces via inheritance so composites can be used wherever a leaf is expected.
- **Encapsulating the formatting algorithm (leading to Strategy)**: pull the linebreaking algorithm out of the glyph structure entirely and into a separate, swappable object.
  - When to use: when an algorithm (here, linebreaking) has multiple competing implementations with different speed/quality trade-offs, and you don't want the choice hard-wired into the data structure it operates on.
  - How: define a `Compositor` abstract class (`SetComposition`, `Compose`); a `Composition` (a `Glyph` subclass holding only unformatted content) is given a `Compositor` instance and calls `Compose` on it when reformatting is needed; the compositor inserts `Row`/`Column` glyphs into the composition's structure.
- **Transparent enclosure (leading to Decorator)**: wrap a glyph in another glyph that adds appearance/behavior (border, scroll bars) while keeping an identical interface, so clients can't tell whether they're dealing with the plain glyph or the embellished one.
  - When to use: whenever you need to add responsibilities to individual objects dynamically, and subclassing for every combination of embellishments (`BorderedScrollableComposition`, etc.) would explode the class count.
  - How: define `MonoGlyph` as a `Glyph` subclass that stores one component and forwards (delegates) every operation to it by default; concrete embellishments (`Border`, `Scroller`) override just the operations they need to augment, calling the parent's forwarding implementation first (or after) to preserve the wrapped object's own behavior.
- **Abstracting object creation (leading to Abstract Factory)**: replace direct constructor calls to concrete look-and-feel widget classes with calls to a factory object's creation methods.
  - When to use: when a whole family of related concrete classes (Motif widgets vs. PM widgets) must be swapped together, and hard-coded constructor calls would scatter platform dependencies throughout the codebase.
  - How: define an abstract `GUIFactory` with one `Create...` operation per product category (`CreateScrollBar`, `CreateButton`); concrete subclasses (`MotifFactory`, `PMFactory`) each instantiate the matching concrete product family; client code holds one factory reference (`guiFactory`) and uses it consistently for all widget creation.
- **Window/WindowImp separation (leading to Bridge)**: split the application-facing `Window` abstraction from the window-system-specific implementation into two independent, separately-varying class hierarchies.
  - When to use: when an abstraction (the concept of a window as Lexi's code understands it) must remain stable while its underlying implementation (X, PM, Macintosh window system calls) needs to vary independently and be swappable, potentially at run-time.
  - How: `Window` and its subclasses (`ApplicationWindow`, `IconWindow`) define the application-facing interface and hold a reference (`_imp`) to an abstract `WindowImp`; concrete `WindowImp` subclasses (`XWindowImp`, `PMWindowImp`) implement the same operations (e.g., `DeviceRect`) in terms of each window system's actual API; a `WindowSystemFactory` (an Abstract Factory) supplies the correct concrete `WindowImp` at construction time.
- **Encapsulating a request (leading to Command)**: represent every user operation (cut, font change, page turn) as an object with a uniform `Execute` interface, instead of hard-coding requests into specific widget subclasses.
  - When to use: when the same logical operation must be triggered from multiple, unrelated UI elements (a menu item and a toolbar button), and you additionally need undo/redo with unlimited history depth.
  - How: define an abstract `Command` class with `Execute`, `Unexecute`, and a run-time-computed `Reversible` predicate; parameterize widgets like `MenuItem` with a `Command` instance rather than subclassing per request; maintain a linear command history with a movable "present" pointer — undo calls `Unexecute` and moves the pointer left, redo calls `Execute` on the command to the right and moves the pointer right.
- **Encapsulating access and traversal (leading to Iterator)**: pull traversal logic (preorder, postorder, array-based, list-based) out of the `Glyph` interface entirely and into a separate hierarchy of iterator objects.
  - When to use: when a structure's internal storage (array vs. linked list) must stay hidden from clients, multiple traversal orders are needed, and more than one traversal must be able to run concurrently over the same structure.
  - How: define an abstract `Iterator` with `First`, `Next`, `IsDone`, `CurrentItem`; concrete iterators (`ArrayIterator`, `ListIterator`) implement access for a specific storage type; compound iterators (`PreorderIterator`) implement traversal order in terms of the glyph-specific iterators, using an internal stack to descend the structure.
- **Encapsulating the analysis (leading to Visitor)**: move analysis logic (spell-checking, hyphenation) out of `Glyph` subclasses entirely and into a separate class hierarchy that "visits" glyphs during a traversal.
  - When to use: when you expect to add new kinds of whole-structure analysis frequently, but the class hierarchy being analyzed (`Glyph` and its subclasses) is comparatively stable and shouldn't be touched for every new analysis.
  - How: give `Glyph` and every subclass one `Accept(Visitor&)` operation that calls back a type-specific method on the visitor (e.g., `Character::Accept` calls `visitor.VisitCharacter(this)`); define an abstract `Visitor` with one `Visit...` method per glyph subclass; concrete visitors (`SpellingCheckingVisitor`, `HyphenationVisitor`) implement only the subset of `Visit...` methods relevant to their analysis.

## Key Concepts
- **Glyph**: the abstract base class for every object — visible or structural — that can appear in the document; unifies text and graphics under one interface so both can be composed and drawn uniformly.
- **Compositor / Composition split**: `Composition` holds unformatted content and structural policy hooks; `Compositor` holds the actual linebreaking algorithm — the split is what lets either side change without touching the other.
- **MonoGlyph**: an abstract single-child `Glyph` subclass that forwards all operations to its one component by default, letting embellishment subclasses override only what they need to add.
- **GUIFactory / concrete factory**: `GUIFactory` defines the abstract product-creation interface; a concrete factory (`MotifFactory`) is bound once (e.g., at startup, based on an environment variable) and used consistently thereafter for all widget creation.
- **Window / WindowImp**: `Window` is the stable, application-facing abstraction; `WindowImp` is the volatile, window-system-facing implementation — the pattern lets one evolve without forcing changes to the other.
- **Command history with a "present" line**: a linear list of executed commands with a movable pointer; undo/redo become simple pointer moves plus `Unexecute`/`Execute` calls, with no arbitrary depth limit.
- **Reversible operation**: a run-time-computed Boolean on `Command` that lets a command opt out of the undo stack if executing it produced no actual effect (e.g., a spurious font change to text already in that font).
- **Preorder/inorder/postorder traversal via a stack of iterators**: a compound iterator (e.g., `PreorderIterator`) doesn't reimplement traversal from scratch — it composes glyph-specific iterators via `CreateIterator` and manages descent/backtrack with an internal stack.
- **Accept / Visit double-dispatch**: `Accept(Visitor&)` on the element calls back a type-specific `Visit...` method on the visitor — this double dispatch is what lets the visitor treat different glyph subclasses specially without any `dynamic_cast` or type-testing.

## Mental Models
- Think of each of Lexi's seven problems as the same move applied to a different axis of variation: "find the thing that changes independently of everything else, and give it its own class." Document structure varies in shape (Composite), formatting varies in algorithm (Strategy), embellishment varies in what's added (Decorator), look-and-feel varies in product family (Abstract Factory), window system varies in implementation (Bridge), user operations vary in what request runs (Command), and analysis varies in what's being computed (Visitor).
- Use Abstract Factory when you already control (or can define) the abstract product classes across a family; reach for Bridge instead when the "product" side is an existing, incompatible vendor hierarchy you can't restructure — this is exactly why GoF reject Abstract Factory for the window-system problem in Section 2.6 despite its surface similarity to the look-and-feel problem.
- Iterator and Visitor are complementary, not competing: Iterator answers "how do I walk the structure without knowing its storage," Visitor answers "how do I do type-specific work at each node without editing the node's class" — Lexi's spelling checker uses both together (a `PreorderIterator` drives traversal, a `Visitor` performs the check).
- MonoGlyph's transparent enclosure is a specific, narrower application of the general Decorator idea: GoF explicitly note that "embellishment" in the full Decorator pattern is broader than UI borders/scrollbars — it applies to anything that adds responsibilities to an object (semantic actions on an AST, new transitions on an automaton).

## Anti-patterns
- **Subclassing for every combination of embellishments**: `BorderedComposition`, `ScrollableComposition`, `BorderedScrollableComposition`, and so on — the class count grows combinatorially and none of it is changeable at run-time; this is the exact problem transparent enclosure (Decorator) solves.
- **Hard-coding concrete widget constructors (`new MotifScrollBar`) throughout the application**: makes porting to a new look-and-feel require finding and changing every such call site, and makes run-time look-and-feel switching impossible — this is what motivates Abstract Factory.
- **Parameterizing menu items with a bare function pointer instead of a command object**: GoF list three concrete failures — no natural place for undo/redo state, no natural place to store request-specific state (e.g., which font to change to), and functions are hard to extend/reuse compared to a class hierarchy — hence Command uses a full object, not a callback.
- **Type-testing/downcasting in an analysis routine** (`dynamic_cast<Character*>(glyph)` chains inside a spelling checker): explicitly called out by GoF as "pretty ugly," reliant on esoteric casts, and requiring a code change every time the `Glyph` hierarchy changes — the motivating failure mode that Visitor's double dispatch eliminates.
- **Putting traversal logic directly inside `Glyph` subclasses via an integer index and an enumerated `Traversal` kind parameter**: can't support new traversal orders without extending the enum or adding operations, can't run two traversals over the same structure concurrently, and biases the interface toward one storage representation — motivates pulling traversal out into a separate `Iterator` hierarchy.

## Code Examples
```cpp
// Bridge: Window delegates to an abstract WindowImp so window-system
// specifics never leak into the application-facing Window hierarchy.
void Window::DrawRect(Coord xO, Coord yO, Coord xl, Coord yl) {
    _imp->DeviceRect(xO, yO, xl, yl);   // _imp is the WindowImp instance
}

// XWindowImp implements DeviceRect in terms of the X Window System's API
void XWindowImp::DeviceRect(Coord xO, Coord yO, Coord xl, Coord yl) {
    int x = round(min(xO, xl));
    int y = round(min(yO, yl));
    int w = round(abs(xO - xl));
    int h = round(abs(yO - yl));
    XDrawRectangle(_dpy, _winid, _gc, x, y, w, h);
}
// PMWindowImp implements the same DeviceRect operation completely
// differently, in terms of Presentation Manager's path-based drawing API —
// Window and its subclasses never need to know or care which is in use.
```
- **What it demonstrates**: the Bridge pattern's core payoff — `Window`'s interface and `WindowImp`'s interface can evolve, and be implemented, completely independently of one another; adding a new window system means adding one new `WindowImp` subclass, never touching `Window`.

## Reference Tables

**Lexi's seven design problems mapped to their resulting pattern(s), from Section 2.9's summary:**

| # | Design Problem (Section) | Core Constraint | Resulting Pattern(s) |
|---|---------------------------|-------------------|------------------------|
| 1 | Document Structure (2.2) | Treat text/graphics and simple/compound elements uniformly | Composite |
| 2 | Formatting (2.3) | Swap linebreaking algorithms without touching document structure | Strategy |
| 3 | Embellishing the UI (2.4) | Add/remove borders and scroll bars without subclass explosion | Decorator |
| 4 | Multiple Look-and-Feel Standards (2.5) | Create whole families of related widgets without naming concrete classes | Abstract Factory |
| 5 | Multiple Window Systems (2.6) | Vary window-system implementation independently of the application-facing abstraction | Bridge |
| 6 | User Operations (2.7) | Trigger the same request from multiple UI elements; support unlimited undo/redo | Command |
| 7 | Spelling Checking and Hyphenation (2.8) | Access scattered text uniformly across differing storage; add analyses without editing Glyph | Iterator + Visitor |

## Worked Example
**Reconstructing Problem 2 (Formatting → Strategy) end-to-end, from Section 2.3:**

**Constraint**: Lexi must break glyphs into lines (and lines into columns, columns into pages) according to a linebreaking algorithm, but different algorithms trade off formatting quality against speed differently (a quick `SimpleCompositor` vs. a slow, high-quality `TeXCompositor` implementing the full TeX algorithm). The document's physical-structure representation (from Problem 1's Composite solution) must stay completely independent of which algorithm is chosen — adding a new `Glyph` subclass shouldn't require touching the formatting code, and adding a new formatting algorithm shouldn't require touching `Glyph` subclasses.

**Reasoning**: Because the algorithm needs to be replaceable — ideally even at run-time — GoF isolate it by defining a *separate class hierarchy* purely for objects that encapsulate a formatting algorithm. The root of that hierarchy defines an interface general enough to support a wide range of algorithms; each subclass implements one specific algorithm. A `Glyph` subclass (`Composition`) is then given one of these algorithm objects and delegates formatting to it whenever formatting is needed.

**Resulting structure**:
- `Compositor` (abstract): interface `SetComposition(Composition*)` and `Compose()`.
- Concrete compositors: `SimpleCompositor`, `TeXCompositor` — each implements `Compose` with a different linebreaking algorithm.
- `Composition` (a `Glyph` subclass): initially holds only the unformatted, visible content glyphs (no `Row`/`Column` yet); is constructed with a `Compositor` instance; calls `compositor->Compose()` whenever reformatting is needed (e.g., the user edits the document).
- `Compose()`'s effect: the compositor iterates through the composition's children and inserts new `Row` and `Column` glyphs per its linebreaking algorithm, producing the object structure that Problem 1's Composite pattern already knows how to draw and traverse.
- Run-time swap: adding a single `SetCompositor` operation to `Composition`'s interface lets the linebreaking algorithm change even after the document exists, without recompiling.

**Why this is Strategy**: the `Compositor` objects are the interchangeable Strategy objects; `Composition` is the Context. The pattern's applicability criterion — interfaces for both strategy and context general enough to support a *range* of algorithms without needing to change either interface per new algorithm — is exactly what `Compositor`'s minimal two-method interface and `Glyph`'s existing child-management interface (`Insert`/`Remove`/`Child`, already established for Composite) achieve here.

## Key Takeaways
1. All seven of Lexi's problems are solved by the same underlying move: identify the concept most likely to change, and give it its own object and class hierarchy, separate from the structure that stays stable.
2. Abstract Factory and Bridge look similar (both decouple from a variability axis) but apply under opposite conditions: Abstract Factory needs you to own the abstract product classes across the family; Bridge is used when the "implementation" side is an existing, incompatible hierarchy you can't unify — check which situation you're in before picking one.
3. Command's undo/redo mechanism needs three things beyond a plain `Execute`: an `Unexecute` counterpart, a run-time `Reversible` check (not everything meaningfully executed is meaningfully undoable), and a linear history with a movable "present" pointer, not just a stack.
4. Iterator and Visitor solve different halves of "process every node in a structure I don't want to hard-code knowledge of": Iterator abstracts *how you walk*, Visitor abstracts *what you do at each stop* — most nontrivial traversal-based features need both, not one or the other.
5. Visitor is the right choice only when the class hierarchy being visited is comparatively stable and the operations performed on it change often; if new element subclasses are added frequently, every visitor implementation needs a matching new `Visit...` method, which flips the trade-off.
6. Transparent enclosure (MonoGlyph) is a narrowly-scoped, concrete instance of the broader Decorator pattern — recognizing the general pattern behind a specific implementation (as GoF explicitly do at the end of Section 2.4) is how you generalize a one-off design trick into a reusable pattern.

## Connects To
- **Ch 11 (Composite)**: Lexi's `Glyph` hierarchy is GoF's own canonical worked example of Composite — the C# book's tree-structure motivation is the same recursive-composition idea developed here in full design-rationale detail.
- **Ch 15 (Strategy)**: the `Compositor`/`Composition` split is the direct ancestor of the C# book's `Context`/`IChoice` example — both isolate a swappable algorithm behind a minimal interface reachable via delegation.
- **Ch 07 (Decorator)**: `MonoGlyph`/`Border`/`Scroller` is GoF's original motivating scenario for Decorator, predating and generalizing into the pattern the C# book implements more abstractly.
- **Ch 05 (Abstract Factory)**: `GUIFactory`/`MotifFactory`/`PMFactory` for widget families, and later `WindowSystemFactory` for `WindowImp` objects, are two separate applications of Abstract Factory within the same case study — worth noting both appear here.
- **Ch 12 (Bridge)**: `Window`/`WindowImp` is GoF's canonical Bridge example; contrast this chapter's Section 2.6 discussion of why Abstract Factory alone doesn't suffice for the window-system problem with the C# book's simpler Bridge motivation.
- **Ch 17 (Command)**: Lexi's `Command`/`Unexecute`/`Reversible`/command-history design is considerably richer than most introductory Command examples and is worth reading before the C# book's chapter for the undo/redo rationale specifically.
- **Ch 18 (Iterator) and Ch 13 (Visitor)**: Section 2.8 is the rare case in the GoF text where two patterns are developed together to solve one problem — read them as a pair, since Lexi's spelling checker needs both to function.
