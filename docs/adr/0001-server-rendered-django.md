# Server-rendered Django, no JavaScript framework

The app is plain server-rendered Django templates with normal form posts and
small inline vanilla-JS enhancements. We rejected a React/SPA stack
deliberately: the app has a handful of screens, two users, and the owner
found React tooling more annoying than valuable. Full-page navigation is
softened with the CSS `@view-transition` rule instead of client-side
routing. Don't "fix" this by introducing a frontend framework; if richer
interactivity is ever needed, the agreed escalation path is htmx over the
same Django views, not an SPA.
