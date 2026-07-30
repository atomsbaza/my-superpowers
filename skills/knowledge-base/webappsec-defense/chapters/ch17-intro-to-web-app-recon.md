# Chapter 17: Introduction to Web Application Reconnaissance

## Core Idea
Web application reconnaissance is the explorative data-gathering phase — building both a technical and a functional/business understanding of an application — that must precede effective hacking or defensive hardening, because you cannot properly prioritize attacks (or defenses) against parts of an application you don't know exist.

## Frameworks Introduced
- **The "map" model of recon**: Recon output should be organized like a topographical map — a structured, traversable collection of data points about an application's code, network structure, and feature set — rather than scattered notes.
  - When to use: From the very first exploration of any target application, before attempting any exploit.
  - How: Record API endpoints, payload shapes, features, integrations, and permission tiers in a consistent hierarchical format (the author uses JSON-like notes); update it continuously as new information is found.
- **Assume partial visibility**: Never assume the visible UI represents the full permission/functionality surface of an application; assume by default you are seeing only a subset.
  - When to use: Whenever testing any application with multiple user roles (customer/teller/banker-style tiers).
  - How: Reason from business logic about what operations *must* exist behind the scenes (e.g., someone must be able to create/close a bank account even though the customer UI is read-mostly) and go looking for the APIs or admin interfaces that perform them.

## Key Concepts
- **Role-based access control (RBAC)**: An authorization model where different user tiers (e.g., customer/teller/banker) are granted different levels of access; nearly all serious applications use tiered permissions rather than one flat access level.
- **Recon (reconnaissance)**: The pre-attack data-gathering phase, valuable to hackers, pen testers, bug bounty hunters, and defenders alike.
- **Functional/business analysis**: Understanding an application's revenue model, user base, and competitive position — necessary to judge which data and features are actually "mission-critical" versus incidental.
- **API endpoint shape**: The schema (field names, types, required/optional, min/max) that an endpoint's request payload conforms to; the chapter's JSON note format explicitly records this.
- **Permission enumeration risk**: Recon techniques themselves (probing for hidden endpoints, brute-forcing) can get an IP banned or trigger legal exposure — recon should only be performed with ownership or written authorization.

## Mental Models
- Think of a web application the way you'd think of a bank's org chart: the public-facing UI is analogous to the customer window, but tellers and bankers have privileged internal tools that never appear in the customer-facing interface — assume every application has an equivalent invisible layer until proven otherwise.
- Use "topography" as the guiding metaphor for note organization: just as land has surface, shape, and hidden features, an application has visible UI, underlying API shape, and hidden administrative/internal functionality — a good map captures all three, not just what's on the surface.
- Treat recon notes as a growing asset, not a one-time snapshot: the map should be revisited and expanded as the tester's understanding deepens, and reused across future engagements against the same target.

## Anti-patterns
- **Treating recon as a low-value/skippable step**: Recon skills alone have limited value, but skipping them means offensive/defensive work proceeds without knowing what attack surface actually exists — wasted effort attacking well-secured areas while weaker ones go unexamined.
- **Assuming the UI equals the full application**: Missing entire classes of API endpoints (moderator/admin-only functionality) because only the customer-facing interface was explored.
- **Unstructured note-taking**: Loose or non-hierarchical notes become unusable once an application's scope grows beyond a handful of endpoints; without structure, testers lose track of what has and hasn't been explored.
- **Recon without authorization**: Performing IP-flagging or legally risky recon techniques (from later chapters) against applications without explicit written permission.

## Code Examples
```json
{
  api_endpoints: {
    sign_up: {
      url: 'mywebsite.com/auth/sign_up',
      method: 'POST',
      shape: {
        username: { type: String, required: true, min: 6, max: 18 },
        password: { type: String, required: true, min: 6, max: 32 },
        referralCode: { type: String, required: false, min: 64, max: 64 }
      }
    },
    sign_in: {
      url: 'mywebsite.com/auth/sign_in',
      method: 'POST',
      shape: {
        username: { type: String, required: true, min: 6, max: 18 },
        password: { type: String, required: true, min: 6, max: 32 }
      }
    },
    reset_password: {
      url: 'mywebsite.com/auth/reset',
      method: 'POST',
      shape: {
        username: { type: String, required: true, min: 6, max: 18 },
        password: { type: String, required: true, min: 6, max: 32 },
        newPassword: { type: String, required: true, min: 6, max: 32 }
      }
    }
  },
  features: {
    comments: {},
    uploads: { file_sharing: {} }
  },
  integrations: {
    oauth: { twitter: {}, facebook: {}, youtube: {} }
  }
}
```
- **What it demonstrates**: The author's preferred JSON-like recon note format — hierarchical, capturing endpoint URL/method/payload shape alongside feature and integration inventories, so the "map" stays searchable and sortable as it grows.

## Reference Tables
Permission tiers for a hypothetical banking application, illustrating RBAC and partial UI visibility:

| User     | Type     | Permissions                                                  |
|----------|----------|---------------------------------------------------------------|
| Customer | External | Log in to website; read account balance via web UI.          |
| Teller   | Internal | Create new accounts when provided paperwork from a customer. |
| Banker   | Internal | Modify existing accounts on behalf of customers.              |

## Worked Example
The chapter walks through a banking application to demonstrate why "assume partial visibility" matters:

1. A customer opens a checking account: staff (tellers) had access to an account-creation application the customer never sees.
2. The customer later requests a savings account by phone: a banker used a different privileged tool to link it to the existing login — again, invisible to the customer UI.
3. The customer cannot close an account online but can request closure in person: this reveals a *delete*-capable internal tool exists, even though the customer-facing API is effectively read-only (balance) plus limited write (bill pay/transfers).
4. From these three observations alone — without ever seeing the internal tooling — a tester can conclude: (a) an RBAC system with at least three tiers exists, (b) create/update/delete APIs for accounts exist somewhere even though the customer UI only exposes read and limited write, and (c) those higher-privilege APIs are the highest-value recon target, since they are used less often and reviewed less by end users.
5. The chapter then generalizes this into the JSON map format so that, as a tester later discovers concrete endpoints matching this hypothesis (e.g., an undocumented `/internal/accounts/:id/close` route), they get recorded in the same structure as the public API map.

## Key Takeaways
1. Build a structured, hierarchical "map" of an application's technology, endpoints, and features before attempting to exploit or defend it.
2. Never assume the visible UI is the complete application — reason from business logic about what privileged operations must exist behind the scenes.
3. RBAC/tiered-permission systems are the default in real applications; recon should specifically hunt for the higher-privilege tiers' hidden APIs.
4. Functional/business understanding (revenue model, user types) is what lets you judge which discovered data and endpoints are actually high-value.
5. Recon carries real legal/operational risk (IP bans, legal action) — always scope it to owned or authorized targets.

## Connects To
- **Ch18-23 (this book's Recon material, global)**: This chapter's "map" concept is the organizing thread for every subsequent recon technique — subdomain discovery, API analysis, dependency fingerprinting, and architecture analysis all produce data that feeds into this same map.
- **Ch24-34 (Offense, global)**: The completed recon map is the direct input for prioritizing which offensive techniques to attempt against which endpoints.
- **Ch35-52 (Defense, global)**: The same partial-visibility principle applies defensively — an engineer should map their own application's hidden/internal surface to find what an attacker would find first.
- **Role-based access control (external concept)**: A standard authorization pattern referenced here informally; treated more rigorously in general access-control literature.
