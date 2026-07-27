# Chapter 26: The Main Component

## Core Idea
`Main` is the ultimate detail and lowest-level policy in every system — the dirtiest component, responsible only for creating and wiring up Factories, Strategies, and dependencies before handing control to the high-level abstract portions of the system, and it should be treated as a plugin the rest of the architecture doesn't depend on.

## Frameworks Introduced
- **Main as plugin**: Treat `Main` as a replaceable plugin to the application — one that sets initial conditions, gathers outside resources, and hands control to high-level policy — rather than as part of the application's core.
  - When to use: Whenever configuring an application for multiple environments (Dev/Test/Production), multiple countries/jurisdictions, or multiple customers.
  - How: Place `Main` behind an architectural boundary; create one `Main` implementation per configuration; let each perform its own setup/injection without changing the high-level system.
- **Dependency Injection confined to Main**: Dependencies should be injected by a DI framework only inside `Main`; once injected, `Main` distributes them manually (without further framework involvement) to the rest of the system.
  - When to use: Any system using a DI framework.
  - How: Configure and resolve the DI graph entirely within `Main`; pass concrete instances downward through constructors/parameters from that point on, keeping the DI framework itself invisible to the rest of the codebase.

## Key Concepts
- **Main component**: The component that creates, coordinates, and oversees all other components; the initial entry point of the system.
- **Ultimate detail**: `Main` is the lowest-level policy — nothing except the operating system depends on it, and it depends on (and knows about) everything needed to bootstrap the system.
- **Factory (in Main)**: An object (e.g., `HtwFactory`) that `Main` uses to instantiate the high-level system by class name, so that changes to the concrete implementation class don't force `Main` to recompile/redeploy.
- **Dirtiest component**: A deliberate characterization of `Main` — it is expected to know about low-level, volatile details (string tables, concrete class names, I/O setup) that the rest of the system must not know about.
- **Configuration as a plugin problem**: Once `Main` is treated as a plugin sitting behind an architectural boundary, supporting multiple configurations becomes a matter of swapping `Main` implementations rather than branching logic inside the core system.

## Mental Models
- Think of `Main` as the outermost circle of the clean architecture — the place where all the frameworks, drivers, and glue code live, deliberately isolated from policy.
- Use "does this code load resources/strings/config for the rest of the system, or does it implement business behavior?" to decide whether code belongs in `Main` or in a higher-level component.
- Think of swapping `Main` components (Dev/Test/Prod, or per-customer) the same way you'd swap any other plugin — the high-level system neither knows nor cares which `Main` invoked it.

## Anti-patterns
- **Letting high-level components depend on Main's setup details**: If business logic reaches back into `Main`'s data (string tables, factory names, environment config), the dependency arrow inverts and the high-level policy becomes coupled to the dirtiest, most volatile component in the system.
- **Passing concrete class references instead of names/factories**: Directly referencing a concrete implementation class in `Main` (rather than constructing it via factory + string name) causes unrelated changes in that class to force `Main` to recompile and redeploy.
- **One-size-fits-all Main**: Trying to encode every environment/customer/jurisdiction variation inside a single `Main` with conditionals, instead of creating a separate `Main` plugin per configuration.

## Code Examples
```java
public static void main(String[] args) throws IOException {
    game = HtwFactory.makeGame("htw.game.HuntTheWumpusFacade", new Main());
    createMap();
    BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
    game.makeRestCommand().execute();
    while (true) {
        System.out.println(game.getPlayerCavern());
        System.out.println("Health: " + hitPoints + " arrows: " + game.getQuiver());
        HuntTheWumpus.Command c = game.makeRestCommand();
        System.out.println(">");
        String command = br.readLine();
        if (command.equalsIgnoreCase("e")) c = game.makeMoveCommand(EAST);
        else if (command.equalsIgnoreCase("w")) c = game.makeMoveCommand(WEST);
        else if (command.equalsIgnoreCase("n")) c = game.makeMoveCommand(NORTH);
        else if (command.equalsIgnoreCase("s")) c = game.makeMoveCommand(SOUTH);
        else if (command.equalsIgnoreCase("r")) c = game.makeRestCommand();
        else if (command.equalsIgnoreCase("sw")) c = game.makeShootCommand(WEST);
        else if (command.equalsIgnoreCase("se")) c = game.makeShootCommand(EAST);
        else if (command.equalsIgnoreCase("sn")) c = game.makeShootCommand(NORTH);
        else if (command.equalsIgnoreCase("ss")) c = game.makeShootCommand(SOUTH);
        else if (command.equalsIgnoreCase("q")) return;
        c.execute();
    }
}
```
- **What it demonstrates**: `Main` creates the concrete game object via a named-class Factory (decoupling `Main` from recompiling when `HuntTheWumpusFacade` changes), owns the I/O loop and raw command parsing, but defers all real game processing to higher-level components it does not implement itself.

## Reference Tables
<!-- no comparison/decision table in this chapter -->

## Worked Example
The Hunt the Wumpus `Main` class holds string tables (`environments`, `shapes`, `cavernTypes`, `adornments`) that the rest of the game logic should never see. Its `main()` method constructs the game via `HtwFactory.makeGame("htw.game.HuntTheWumpusFacade", new Main())` — passing the concrete class name as a string rather than referencing the class directly, so changes to `HuntTheWumpusFacade` don't force `Main` to recompile. `main()` also owns `createMap()`, which randomly generates caverns and populates the Wumpus, bats, pits, and player start position by calling into the `game` object's setup API. Everything after setup — command interpretation via `game.makeMoveCommand()`/`makeShootCommand()` — is handed off to the high-level `HuntTheWumpus` abstraction; `Main` itself contains zero game rules.

## Key Takeaways
1. Keep `Main` as the single place where DI frameworks, factories, and concrete class wiring live — resolve the graph there, then pass plain objects downward.
2. Use factory calls with string class names (not direct references) in `Main` to avoid forcing `Main` to recompile/redeploy when concrete implementation classes change.
3. Never let high-level policy depend on anything defined inside `Main` — the dependency arrow must always point from `Main` inward, never the reverse.
4. Treat `Main` as a swappable plugin: one `Main` per environment (Dev/Test/Prod) or per customer/jurisdiction, rather than branching configuration logic inside a shared core.
5. It's acceptable — expected — for `Main` to be "dirty": string tables, I/O setup, and environment-specific detail belong there precisely so they don't pollute the rest of the system.

## Connects To
- **Ch 25 (Layers and Boundaries)**: `Main` sits at the point where all the boundary-crossing dependencies established in Ch 25 are actually wired together.
- **Ch 28 (The Test Boundary)**: Test suites often need their own `Main`-equivalent entry point/bootstrap, following the same plugin principle.
- **Dependency Injection frameworks**: The chapter's guidance to confine DI resolution to `Main` is a direct, practical application of the Dependency Rule to DI tooling specifically.
