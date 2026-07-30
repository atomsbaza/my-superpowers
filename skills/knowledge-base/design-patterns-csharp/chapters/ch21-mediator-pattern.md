# Chapter 21: Mediator Pattern

## Core Idea
Define an object that encapsulates how a set of objects interact, promoting loose coupling by keeping those objects from referring to each other explicitly and letting you vary their interaction independently.

## Frameworks Introduced
- **Mediator**: Define an object that encapsulates how a set of objects interact. Mediator promotes loose coupling by keeping objects from referring to each other explicitly, and it lets you vary their interaction independently (GoF).
  - When to use: A group of objects needs to communicate, but direct references among all of them would create a tangled many-to-many web of dependencies that is hard to change or extend.
  - How: A `Mediator` interface defines the communication contract; a `ConcreteMediator` maintains the list of `Colleague` objects and coordinates their interaction; each `Colleague` talks only to the mediator, never directly to another colleague.

## Key Concepts
- **Mediator**: The interface that defines how communication among colleague objects happens.
- **ConcreteMediator**: Knows and maintains the list of colleague objects, implements the `Mediator` interface, and coordinates communication among them.
- **Colleague**: The interface for an object that communicates with others only through the mediator.
- **ConcreteColleague**: A concrete implementation of `Colleague`; communicates with other colleagues exclusively through the mediator.
- **Registration**: Colleagues must register themselves with the mediator before they are allowed to participate — an unregistered "outsider" is refused.
- **Centralized control logic**: In the modified example, the mediator alone tracks each participant's online/offline status and decides whether a message can be delivered.
- **Many-to-many vs. one-to-many**: The pattern's central trade — it replaces a many-to-many relationship between colleagues with a one-to-many relationship centered on the mediator.

## Mental Models
- Think of the Mediator as an airport control tower: pilots of different airplanes do not talk to each other directly — they report status to the tower, and the tower alone decides who can take off or land. The tower does not control the entire flight, only coordination within its own terminal area.
- Use a Mediator when a form's fields have interdependent enable/disable logic (e.g., a submit button that must stay disabled until user ID, password, and email are all valid) — centralizing that logic in one object avoids scattering conditional checks across every field's code.
- "Without a mediator" vs. "with a mediator": without one, every participant must check every other participant's status before communicating, and the number of interconnections grows unmanageably as participants are added; with one, each participant only ever talks to the mediator, and the mediator owns the status-checking logic.
- The book explicitly frames the Mediator pattern as a "multiplexed Facade" (citing Steve Holzner) — where Facade provides one simplified interface to a single subsystem, Mediator provides a shared interface among multiple peer objects.

## Anti-patterns
- **Letting colleagues reference each other directly "for simplicity"**: works fine with three participants but becomes unmanageable as the group grows, since every object must independently track every other object's state (e.g., online/offline) before it can communicate.
- **Skipping registration checks**: allowing any object to participate without registering removes the mediator's ability to enforce membership and control who is part of the interaction.
- **Letting the mediator become a monolith**: cramming all coordination and status logic into one `ConcreteMediator` without care can make the mediator itself hard to maintain — the pattern moves complexity, it doesn't eliminate it.

## Code Examples
```csharp
interface IMediator
{
    void Register(Friend friend);
    void Send(Friend friend, string msg);
}
// ConcreteMediator
class ConcreteMediator : IMediator
{
    List<Friend> participants = new List<Friend>();
    public void Register(Friend friend)
    {
        participants.Add(friend);
    }
    public void Send(Friend friend, string msg)
    {
        if (participants.Contains(friend))
        {
            Console.WriteLine(String.Format("[{0}] posts: {1} Last message posted {2}",
                friend.Name, msg, DateTime.Now));
            System.Threading.Thread.Sleep(1000);
        }
        else
        {
            Console.WriteLine("An outsider named {0} trying to send some messages", friend.Name);
        }
    }
}
// Friend
abstract class Friend
{
    protected IMediator mediator;
    private string name;
    public string Name { get { return name; } set { name = value; } }
    public Friend(IMediator mediator) { this.mediator = mediator; }
}
```
- **What it demonstrates**: The core Mediator/Colleague structure — colleagues (`Friend` subclasses) never reference each other; they only hold a reference to `IMediator` and route every message through `Send`, which itself checks membership before allowing communication.

```csharp
// ConcreteMediator with per-colleague online/offline state
public void Send(Friend fromFriend, Friend toFriend, string msg)
{
    if (toFriend.Status == "On")
    {
        Console.WriteLine(String.Format("[{0}->{1}] : {2} Last message posted {3}",
            fromFriend.Name, toFriend.Name, msg, DateTime.Now));
        System.Threading.Thread.Sleep(1000);
    }
    else
    {
        Console.WriteLine(String.Format("[{0}->{1}] : {2}, you cannot post messages now. {3} is offline.",
            fromFriend.Name, toFriend.Name, fromFriend.Name, toFriend.Name));
    }
}
```
- **What it demonstrates**: The modified mediator now owns targeted delivery logic (`fromFriend` to `toFriend`) plus a status check, showing how coordination complexity concentrates in the mediator rather than being duplicated across colleagues.

## Reference Tables
| Without Mediator | With Mediator |
|---|---|
| Every participant must check every other participant's status before sending | Only the mediator checks status |
| Many-to-many interconnections | One-to-many (each colleague ↔ mediator) |
| Adding a participant means updating everyone else's logic | Adding a participant means registering it with the mediator |

## Worked Example
Three friends — Amit, Sohel, and Raghu (the boss) — register with a `ConcreteMediator` over a shared chat server. The mediator lists all registered participants, then Amit sends a message to the group, Sohel replies, and Raghu tells them to get back to work — each `Send` call is routed and stamped through the mediator. An unregistered friend, Jack, then tries to post and is rejected with "An outsider named Jack trying to send some messages," since he never called `Register`. In the Q&A's modified version, each `Friend` gains a `Status` ("On"/"Off"), and `Send` now takes both a sender and a target; the mediator only delivers a message if the target's status is "On" — demonstrated by Sohel going offline (her incoming message is refused) and Amit later going offline (Raghu's message to him is refused) while messages to still-online participants succeed.

## Key Takeaways
1. Mediator reduces the complexity of inter-object communication by replacing many-to-many references with a single one-to-many hub.
2. It promotes loose coupling and reusability of colleague objects, since they depend only on the mediator's interface, not on each other's concrete types.
3. It can be described as a "multiplexed Facade" — Facade simplifies access to one subsystem; Mediator simplifies interaction among many peer objects.
4. The main risk is that the mediator itself can become a complex, hard-to-maintain god object if too much coordination logic accumulates in one place.
5. This code targets pre-modern C# (2018, .NET Framework era) — the pattern's coordination-hub intent still applies today, but idiomatic C# might favor an event-aggregator, `IObservable<T>`, or reactive/pub-sub mechanism over hand-rolled registration lists.

## Connects To
- **Ch 14 (Observer)**: The book explicitly contrasts the two — in Observer, all registered subscribers are notified in parallel and independently, whereas in Mediator, the mediator actively coordinates and controls the interaction (e.g., checking online status) rather than merely broadcasting.
- **Facade (not covered in these chapters but referenced)**: Mediator is described as a "multiplexed Facade" — the same idea of hiding subsystem complexity behind one entry point, but applied to peer-to-peer interaction rather than a single subsystem.
- **GoF 1994 catalog**: Mediator is one of the Behavioral patterns in the original Gang of Four catalog.
