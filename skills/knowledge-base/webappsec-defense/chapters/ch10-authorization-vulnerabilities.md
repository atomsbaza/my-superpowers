# Chapter 10: Authorization Vulnerabilities

## Core Idea
Authorization is domain logic, not boilerplate — there's no universal recipe ("draw-the-rest-of-the-owl problem"), so consistent modeling (RBAC/ABAC), disciplined code organization, deliberate failure responses, and rigorous testing are what prevent the hardest bug class in security: sins of omission.

## Frameworks Introduced
- **RBAC (role-based access control) + ABAC (attribute-based access control)**: most real applications need both — RBAC defines what category of user someone is, ABAC defines which specific objects they can act on.
  - When to use: RBAC for coarse permissions (regular user / moderator / admin); ABAC for per-resource ownership checks (this post belongs to this user).
  - How: assign roles to users; separately check subject-object-policy relationships (e.g., "is `current_user` the author of `post`?") before permitting an action.
- **Interceptor pattern (decorators/hooks/filters)**: wrap HTTP-handling functions with an authorization check that runs before the handler.
  - When to use: static/centralized routing (most frameworks), where dynamic routing tables aren't available.
  - How: use language-level decorators (Python `@authenticate`), framework hooks (Rails before_action), or servlet `Filter`/`filter-mapping` config bound to URL prefixes like `/admin/*`.
  - When to use dynamic routing tables instead: frameworks like Rails that let you construct the route table itself at runtime based on auth state, keeping unauthorized routes from existing at all.
- **Deliberate authorization-failure responses (302 / 403 / 404)**: choosing the HTTP status code is itself a security decision.
  - When to use: 302 redirect to login when unauthenticated; 403 Forbidden when authenticated but not permitted and existence can be acknowledged; 404 Not Found when even acknowledging the resource's existence would leak sensitive information (e.g., admin URLs).
  - How: raise a domain-specific exception in the Model layer, translate it into the correct status code in the Controller layer.

## Key Concepts
- **Authentication vs. authorization vs. access control**: access control is the umbrella term; authentication answers "who are you," authorization answers "what can you do."
- **Draw-the-rest-of-the-owl problem**: security literature is clear that authorization matters but offers little concrete guidance, because authorization rules are inherently domain-specific.
- **Domain logic**: the part of an application's code that is unique to solving its users' specific problem, as opposed to generic session/templating/DB-connection code.
- **Trust boundary**: the line between validated (trusted) and unvalidated (untrusted) input; mixing both in one data structure causes authorization bugs.
- **Vertical escalation**: an attacker manipulates input to gain a higher privilege level than they should have.
- **Horizontal escalation**: an attacker changes their apparent identity to act as another user at the same privilege level.
- **MVC (Model-View-Controller)**: an architecture where authorization decisions belong in the Model (domain logic) and get translated to HTTP responses by the Controller.

## Mental Models
- Think of authorization rules as a living design document, not just code — write down "who can do what" outside the codebase first, since the code alone won't communicate intent to reviewers or new team members.
- Use a clean, prefixed URL scheme (`/admin`, `/api`) as a forcing function: an admin URL without an access-control check should "stick out like a sore thumb" during review.
- Client-side (JavaScript) authorization is a UX nicety, never a security boundary — every server-side endpoint must independently re-check authorization because an attacker can freely modify browser-side code.
- Remember the time dimension: authorization isn't static — trials expire, subscriptions lapse, embargoed financial reports must not be accessible before their release time.

## Anti-patterns
- **Missing access-control checks**: the hardest class of bug to catch because nothing is there to trigger a test failure — mitigate with deliberate unit-test coverage of every privileged action.
- **Confusion about which component enforces access control**: mixing URL-level, model-level, and interceptor-level checks across a codebase creates gaps where each layer assumes another layer already checked.
- **Mixing trusted and untrusted data in the same structure**: e.g., storing an unvalidated access claim in the same session object as trusted user data — other code/developers may not know the claim wasn't validated.
- **Deciding authorization based on attacker-manipulable input**: any authorization decision derived from unvalidated HTTP input opens the door to vertical or horizontal escalation.
- **Acknowledging sensitive URL existence via 403 instead of 404**: for highly sensitive paths (e.g., `/admin/business-plans/...`), even a 403 leaks that the resource exists — return 404 instead.

## Code Examples
```ruby
Rails.application.routes.draw do
  unless is_authenticated?
    root 'static#home'
    get  'login', to: 'authentication#login'
    post 'login', to: 'authentication#login'
    get  'profile', to: redirect('/login')
  end
  if is_authenticated?
    root 'feed#home'
    get   'login',   to: redirect('/profile')
    get   'profile', to: 'user#profile'
    post  'profile', to: 'user#profile'
    if is_admin?
      get 'admin', to: 'admin#home'
      put 'admin', to: 'admin#home'
    end
  end
end
```
- **What it demonstrates**: dynamic routing table — unauthorized routes simply don't exist at runtime, rather than existing and being blocked.

```python
def authenticate(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_token = request.headers.get('Authorization')
        if not auth_token:
            return jsonify({'message': 'Authorization token missing.'}), 401
        if not validate_token(auth_token):
            return jsonify({'message': 'Invalid authorization token.'}), 401
        return func(*args, **kwargs)
    return wrapper
```
- **What it demonstrates**: interceptor pattern via a Python decorator, checked before the wrapped handler runs.

```java
public class Post {
    public void edit(User user, String newContent) {
        if (!post.getAuthor().equals(user)) {
            throw new IllegalEditException("You can only edit your own posts");
        }
        post.setContent(newContent);
    }
}

@Consumes(MediaType.APPLICATION_JSON)
@Produces(MediaType.TEXT_PLAIN)
public Response editPost(EditRequest changes) {
    try {
        User user = this.getCurrentUser();
        Post post = this.getPost(changes.getPostId());
        post.editPost(user, changes.getContent());
        post.save();
        return Response.ok("Post edited successfully!").build();
    } catch (IllegalEditException e) {
        return Response.status(Status.FORBIDDEN).entity(e.getMessage()).build();
    }
}
```
- **What it demonstrates**: MVC pattern — authorization check and exception live in the Model (`Post`), the Controller translates the exception into an HTTP 403.

```python
@patch('app.db')
@patch('app.current_user')
def test_illegal_edit(self, db, current_user):
    current_user.return_value = User(id: 1, username: 'notTheAuthor')
    db.get_post.return_value = Post(
        title: 'Original Title', content: 'Original Content',
        owner: User(id: 2, username: 'theAuthor'))
    response = self.client.put('/post/1', json={
        'title': 'Updated Title', 'content': 'Updated content'})
    self.assertEqual(response.status_code, 401)
    db.session.commit.assert_not_called()
```
- **What it demonstrates**: mocking database and current-user context to unit-test an authorization failure path without touching real infrastructure.

## Reference Tables
| Failure scenario | Response code | Rationale |
|---|---|---|
| Not authenticated, page requires login | 302 Redirect (to login, with `next` param) | User just needs to log in; no info leaked |
| Authenticated but not permitted | 403 Forbidden | OK to acknowledge the resource exists |
| Resource is sensitive enough that existence itself is secret | 404 Not Found | Prevents leaking that admin/sensitive paths even exist |

| Case study | Roles | Key ABAC check |
|---|---|---|
| Web forum (Reddit-like) | regular user / moderator / admin | can a user delete only their own comment? |
| Content platform (CMS) | reader / writer / editor | is content published, or owned by the requesting writer? |
| Messaging tool | any user, friend-scoped | is the requester a participant in this conversation? |

## Worked Example
The content-platform (CMS) case study: readers can view only published content; writers have reader permissions plus the ability to submit content, which is stored as unpublished and visible only to the submitting writer and to editors; editors can additionally view unpublished content, request writer changes, and promote content to published status.

Implementing this requires ABAC layered on RBAC: the role (reader/writer/editor) determines the *category* of allowed actions, but the object's `status` attribute (published/unpublished) and its `author` attribute determine whether a *specific* piece of content is visible to a *specific* user. A writer requesting `GET /articles/42` must be checked against both — their role must allow reading unpublished content only if `article.author == current_user`, while an editor's role bypasses the author check entirely. Instagram's real-world lesson is directly relevant here: a seemingly small attribute (whether "likes" counted as published/visible content) was authorized incorrectly, publicly exposing something users expected to be private — illustrating why the authorization design document must be updated whenever a new feature touches an existing resource's visibility rules.

## Key Takeaways
1. Document authorization rules as domain logic in a living design doc, outside the code, before implementing them.
2. Model authorization as a mix of RBAC (role) and ABAC (resource-attribute) checks — most real systems need both.
3. Design your URL scheme deliberately (`/admin`, `/api` prefixes) so missing checks are visually obvious.
4. Put authorization decisions in the Model layer under MVC; let the Controller translate exceptions into HTTP status codes.
5. Choose 302 vs. 403 vs. 404 deliberately based on whether resource existence itself is sensitive.
6. Prioritize unit tests for every privileged/sensitive action — missing-check bugs are invisible without them.
7. Never mix trusted and untrusted data in one structure, and never base an authorization decision on unvalidated input.

## Connects To
- **Ch 8/9**: authorization builds directly on authentication and session identity — a broken session makes every authorization check moot.
- **Ch 11**: mass assignment vulnerabilities are effectively an authorization failure (overwriting fields like `isAdmin` that should be access-controlled).
- **Secure by Design (Johnsson, Deogun, Sawano)**: recommended further reading for structuring authorization within MVC.
