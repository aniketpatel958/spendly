# Spec: Profile Page

## Overview
The profile page is the first logged-in-only page in Spendly. It gives an
authenticated user a personal home that confirms who they're signed in as and
summarises their spending at a glance: account details (name, email, member
since) plus an expense summary (total spent, number of expenses, and a
per-category breakdown) drawn from their seeded/own expenses. It exists at this
point in the roadmap because login (step 03) is now complete — there is a real
session to read from — but the expense CRUD flows (steps 07–09) don't exist
yet, so this page is **read-only**. It also establishes the **login-required
guard** pattern that every later protected page will reuse.

## Depends on
- **Step 01 — Database setup**: `users` and `expenses` tables, `get_db()`.
- **Step 03 — Login and Logout**: a working session storing
  `session['user_id']` and `session['user_name']`, plus the already-logged-in
  redirect pattern used by `/login` and `/register`. Profile reads `user_id`
  from the session and must redirect anonymous visitors to `/login`.

## Routes
- `GET /profile` — fetch the logged-in user's account info and expense summary,
  render `profile.html`; redirect to `/login` if not authenticated —
  **logged-in only**

This replaces the current stub (`return "Profile page — coming in Step 4"` in
`app.py`). No other routes change.

## Database changes
No schema changes — `users` and `expenses` already have every column needed
(`users`: id, name, email, password_hash, created_at; `expenses`: id, user_id,
amount, category, date, description, created_at).

Two **read helpers** will be added to `database/db.py` (no inline SQL in the
route):
- `get_user_by_id(user_id)` — returns the user row (`id`, `name`, `email`,
  `created_at`, …) or `None`. Mirrors the existing `get_user_by_email`.
- `get_expense_summary(user_id)` — returns aggregate spending for one user:
  total amount spent, expense count, and a per-category breakdown
  (category → summed amount), computed with SQL aggregation
  (`SUM(amount)`, `COUNT(*)`, `GROUP BY category`). Returns sensible zero/empty
  values when the user has no expenses.

(Optionally, a `get_expenses_by_user(user_id)` helper returning the user's most
recent expense rows may back a small "recent activity" list on the page — keep
it in `db.py` if added.)

## Templates
- **Create:**
  - `templates/profile.html` — extends `base.html`; renders the account card
    (name, email, member-since) and the expense summary (total, count,
    per-category breakdown). Uses `{% block head %}` to link the new
    page-specific stylesheet.
- **Modify:**
  - `templates/base.html` — make the logged-in `session.user_name` in the nav a
    link to `url_for('profile')` (currently it's a plain `<span>`), so the page
    is reachable. Keep the logged-out nav unchanged.

## Files to change
- `app.py` — implement the `/profile` view: login guard
  (`if not session.get("user_id"): return redirect(url_for("login"))`), call
  `get_user_by_id` + `get_expense_summary`, render `profile.html` with that
  data. Replace the stub.
- `database/db.py` — add `get_user_by_id(user_id)` and
  `get_expense_summary(user_id)` (and optionally `get_expenses_by_user`).
- `templates/base.html` — link the nav username to the profile page.
- `CLAUDE.md` — flip the `/profile` route-table row from "Stub — Step 4" to
  implemented.

## Files to create
- `templates/profile.html`
- `static/css/profile.css`

## New dependencies
No new dependencies. Everything uses Flask, Jinja2, and stdlib `sqlite3`
already in `requirements.txt`.

## Rules for implementation
- No SQLAlchemy or ORMs — raw `sqlite3` via `get_db()` only.
- Parameterised queries only (`?` placeholders) — never f-strings in SQL.
- Passwords hashed with werkzeug — never expose `password_hash` to the template
  or page; the profile must not render the hash.
- All DB access lives in `database/db.py` — the route only fetches data and
  renders. No inline SQL or aggregation logic in `app.py`.
- Use CSS variables (`--ink`, `--paper-card`, `--accent`, `--border`,
  `--radius-md`, etc.) — never hardcode hex values. Page-specific styles go in
  `static/css/profile.css`, not inline `<style>` and not dumped into
  `style.css`.
- All templates extend `base.html`; every internal link uses `url_for()`.
- The login guard must redirect anonymous users to `url_for('login')` (do not
  `abort(401)` — match the app's redirect-based auth UX).
- Amounts are displayed formatted (e.g. two decimal places); formatting happens
  in the template/route, not by changing stored values.
- Reuse existing component classes where they fit (`.nav-*`, `.flash`, card and
  button patterns); the implementation may use the `spendly-ui-designer`
  frontend-design skill to produce the page's visual design within these
  constraints.

## Definition of done
- [ ] Visiting `/profile` while **not** logged in redirects to `/login` (no
      stub text, no traceback).
- [ ] Visiting `/profile` while logged in (e.g. as `demo@spendly.com`) renders
      `profile.html` — no plain-text stub remains.
- [ ] The page shows the logged-in user's **name**, **email**, and a
      **member-since** value derived from `users.created_at`.
- [ ] The page shows an **expense summary**: total amount spent and number of
      expenses for that user (for the demo user: 8 expenses totalling 282.64).
- [ ] The page shows a **per-category breakdown** of spending (each category
      with its summed amount), driven by `get_expense_summary`.
- [ ] A user with no expenses sees a sensible empty/zero state, not an error.
- [ ] The `password_hash` is never rendered anywhere on the page.
- [ ] The nav username links to `/profile`, and the link works from any page
      while logged in.
- [ ] All new SQL is parameterised and lives in `database/db.py`; the route
      contains no inline SQL.
- [ ] Styling comes from `static/css/profile.css` using CSS variables; no
      hardcoded hex and no inline `<style>`.
- [ ] App still runs on port 5001 with `python app.py`.
