# Chapter 8: Adapter Pattern

## Core Idea
Convert the interface of a class into another interface that clients expect. Adapter lets classes work together that otherwise couldn't, because of incompatible interfaces.

## Frameworks Introduced
- **Adapter**: Convert the interface of a class into another interface that clients expect, letting otherwise-incompatible classes work together.
  - When to use: You have an existing type whose interface doesn't match what a client (or another API) expects, and you can't or don't want to change either side.
  - How: Create an adapter class that implements the target interface (`RectInterface`) and internally holds/wraps the incompatible type (`Triangle`), translating each target-interface call into a call the wrapped type actually understands.

## Key Concepts
- **Target interface**: The interface the client already knows how to call (`RectInterface`), which the adapter must implement.
- **Adaptee**: The existing, incompatible type being adapted (`Triangle`) — its interface is what the client cannot call directly.
- **Adapter**: The class that implements the target interface and translates calls into equivalent calls on the adaptee (`TriangleAdapter` implements `RectInterface` and holds a `Triangle`).
- **Object adapter**: Adapts via object composition — the adapter holds an instance of the adaptee and delegates to it. This is what C# uses when multiple inheritance isn't available.
- **Class adapter**: Adapts via subclassing (multiple inheritance of implementation) — since C# classes can't multiple-inherit, a class adapter can only subclass the adaptee and implement the target interface alongside it.
- **Interface segregation from concrete classes**: The modified example moves from concrete `Rect`/`Triangle` classes to `RectInterface`/`TriInterface`, reflecting the OO principle of depending on interfaces, not concrete types.

## Mental Models
- Think of an AC power adapter used in international travel: it doesn't change your laptop or the wall socket, it sits between them so two otherwise-incompatible interfaces can connect.
- A translator converting one spoken language into another is doing the same job: making two parties that can't otherwise communicate work together, without changing either party.
- Use Adapter specifically when the two things being connected are *similar enough* that the conversion is meaningful (the book's own example: a triangle's area formula can meaningfully stand in for a rectangle's). Do not use it to force together things that aren't actually alike (see Anti-patterns).

## Anti-patterns
- **Adapting between fundamentally different concepts**: The book explicitly warns against, e.g., "converting a circle to a rectangle" to compute an area — triangles and rectangles have enough structural similarity (base × height factors) for the conversion to make sense; a circle does not share that structure, so forcing the adaptation produces a meaningless result (chapter Note).
- **Reaching for a class adapter without checking constraints**: C# offers no multiple inheritance for classes, so a "class adapter" can only be built by subclassing the adaptee directly and implementing the target interface on top — that's not always possible (e.g., adapting a method not expressible through a C# interface), which is why object adapters (composition) are the more broadly usable choice (Q1, Q2).

## Code Examples
```csharp
using System;
namespace AdapterPattern_Modified
{
    interface RectInterface
    {
        void AboutRectangle();
        double CalculateAreaOfRectangle();
    }

    class Rect : RectInterface
    {
        public double Length;
        public double Width;
        public Rect(double l, double w)
        {
            this.Length = l;
            this.Width = w;
        }
        public double CalculateAreaOfRectangle()
        {
            return Length * Width;
        }
        public void AboutRectangle()
        {
            Console.WriteLine("Actually, I am a Rectangle");
        }
    }

    interface TriInterface
    {
        void AboutTriangle();
        double CalculateAreaOfTriangle();
    }

    class Triangle : TriInterface
    {
        public double BaseLength;//base
        public double Height;//height
        public Triangle(double b, double h)
        {
            this.BaseLength = b;
            this.Height = h;
        }
        public double CalculateAreaOfTriangle()
        {
            return 0.5 * BaseLength * Height;
        }
        public void AboutTriangle()
        {
            Console.WriteLine("Actually, I am a Triangle");
        }
    }

    /*TriangleAdapter is implementing RectInterface. So, it needs to
    implement all the methods defined in the target interface.*/
    class TriangleAdapter : RectInterface
    {
        Triangle triangle;
        public TriangleAdapter(Triangle t)
        {
            this.triangle = t;
        }
        public void AboutRectangle()
        {
            triangle.AboutTriangle();
        }
        public double CalculateAreaOfRectangle()
        {
            return triangle.CalculateAreaOfTriangle();
        }
    }

    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("***Adapter Pattern Modified Demo***\n");
            //CalculatorAdapter cal = new CalculatorAdapter();
            Rect r = new Rect(20, 10);
            Console.WriteLine("Area of Rectangle is :{0} Square unit", r.CalculateAreaOfRectangle());
            Triangle t = new Triangle(20, 10);
            Console.WriteLine("Area of Triangle is :{0} Square unit", t.CalculateAreaOfTriangle());
            RectInterface adapter = new TriangleAdapter(t);
            //Passing a Triangle instead of a Rectangle
            Console.WriteLine("Area of Triangle using the triangle adapter is :{0} Square unit", GetArea(adapter));
            Console.ReadKey();
        }
        /*GetArea(RectInterface r) method  does not know that through
        TriangleAdapter, it is getting a Triangle instead of a Rectangle*/
        static double GetArea(RectInterface r)
        {
            r.AboutRectangle();
            return r.CalculateAreaOfRectangle();
        }
    }
}
```
- **What it demonstrates**: `GetArea(RectInterface r)` accepts a `TriangleAdapter` without any awareness it's actually operating on a `Triangle` — the adapter satisfies `RectInterface` while translating every call into the `Triangle`'s own methods.

## Reference Tables
Class adapter vs. object adapter (from the "Types of Adapters" section):

| Aspect | Class Adapter | Object Adapter |
|---|---|---|
| Mechanism | Subclassing (multiple inheritance of implementation) | Object composition (holds an adaptee instance) |
| C# support | Limited — classes can't multiple-inherit; only viable by subclassing the adaptee directly | Fully supported, the book's preferred approach |
| Flexibility | Less flexible, tied to a fixed base class | More flexible, adaptee can be swapped/passed in |
| Book's preference | Not preferred | Preferred — "in most cases I prefer compositions over inheritance" (Q2) |

## Worked Example
The original illustration: a `Calculator.GetArea(Rect)` method only knows how to compute rectangle area. To reuse it for triangles, a `CalculatorAdapter.GetArea(Triangle)` method converts the triangle's base/height into an equivalent `Rect` (`rect.length = triangle.baseT; rect.width = 0.5 * triangle.height;`) and delegates to `Calculator.GetArea`. Running it with a triangle of base 20 and height 10 prints `Area of Triangle is 100 Square unit`.

The modified version (shown above) removes concrete-class coupling: `Rect` implements `RectInterface`, `Triangle` implements `TriInterface`, and `TriangleAdapter` implements `RectInterface` while holding a `Triangle`. Running the demo with `Rect(20,10)` and `Triangle(20,10)` prints the rectangle's own area (200), the triangle's own area (100), and then — via `GetArea(adapter)` where `adapter` is a `TriangleAdapter` wrapping the triangle — prints `"Actually, I am a Triangle"` followed by `"Area of Triangle using the triangle adapter is :100 Square unit"`. The book notes you could modify `CalculateAreaOfRectangle()` inside the adapter to multiply by 2.0 (yielding 200, matching a rectangle of the same dimensions) — showing the adapter isn't limited to a pure passthrough; it can reshape the value as needed as long as the two concepts are genuinely comparable.

## Key Takeaways
1. Adapter changes the interface presented to the client without changing either the client or the adapted (adaptee) class.
2. Prefer object adapters (composition) over class adapters (subclassing) in C#, since classes can't multiple-inherit and composition is more flexible anyway.
3. Only adapt between things that are structurally similar enough for the conversion to be meaningful — adapting unrelated concepts (the book's circle-to-rectangle example) produces a nonsensical result even though it compiles.
4. Neither side of the adaptation needs to know about the other: `GetArea(RectInterface r)` never learns it's actually working with a `Triangle`.
5. This example predates modern C# (2018-era, targeting C# 6/7): it uses classic interfaces and constructors with no records, primary constructors, or pattern matching — the Adapter intent still applies, but idiomatic modern C# would express some of this more tersely (see modern-csharp-notes.md).

## Connects To
- **Ch 6 (Proxy) / Ch 7 (Decorator)**: All three wrap an object behind delegation, but the intents differ sharply — Proxy controls access to an unchanged interface, Decorator adds responsibilities to an unchanged interface, and Adapter is the odd one out: it deliberately *changes* the interface so two incompatible types can cooperate.
- **Ch 9 (Facade)**: Frequently confused with Adapter, but the book draws the line explicitly (Q4): Adapter alters an interface so clients see no difference between interfaces; Facade simplifies a complex subsystem's interface rather than converting one interface into another.
- **GoF 1994 catalog**: Adapter is one of the seven original Structural patterns.
