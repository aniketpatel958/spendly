# Spec: Login and Logout

## Overview
This feature lets an existing Spendly user authenticate with their email and
password and establishes a logged-in session, plus a logout action that ends
that session. Registration (step 02) creates accounts and hashes passwords;
this step is the other half of the auth loop — it verifies credentials against
the stored `password_hash`, stores the user's id in the Flask `session`, and
gives the user a way to sign out. It is the prerequisite for every
logged-in-only page that follows (profile, expenses).

## Depends on
- **Step 01 — Database setup**: `users` table with `password_hash` column,
  `get_db()`, `init_db()`, `seed_db()`.
- **Step 02 — Registration**: accounts must be creatable (POST `/register`
  inserting a hashed password) so there is something to log in against. The
  `users` table schema and `generate_password_hash` usage from registration are
  mirrored here. Note: if step 02 is not yet merged into `main`, only the
  seeded demo user (`demo@spendly.com` / `demo123`) will be loginable.

## Routes
- `POST /login` — verify submitted email + password, set `session['user_id']`
  on success, re-render `login.html` with an error on failure — public
- `GET /logout` — clear the session and redirect to the landing page —
  logged-in (no-op safe if not logged in)

Note: `GET /login` already exists (renders `login.html`). This step adds the
`POST` handler to the same `login` view function and replaces the `/logout`
stub.

## Database changes
No database changes. The `users` table already has the columns needed
(`id`, `name`, `email`, `password_hash`).

A read helper will be **added to `database/db.py`** (not the schema):
- `get_user_by_email(email)` — returns the user row (or `None`) for credential
  verification.

## Templates
- **Create:** none.
- **Modify:**
  - `templates/base.html` — add a flashed-messages block (Jinja
    `get_flashed_messages()`); swap the static "Sign in / Get started" nav links
    so that when `session['user_id']` is set, the nav shows the user and a
    logout link (`url_for('logout')`) instead.
  - `templates/login.html` — already scaffolded (POSTs to `/login`, fields
    `email` + `password`, `{% if error %}` block). Change the hardcoded
    `action="/login"` to `action="{{ url_for('login') }}"` per project rules.

## Files to change
- `app.py` — add imports (`request`, `session`, `redirect`, `url_for`, `flash`,
  `abort`), set `app.secret_key`, implement `POST` in the `login` view, replace
  the `/logout` stub.
- `database/db.py` — add `get_user_by_email(email)`.
- `templates/base.html` — flash block + session-aware nav.
- `templates/login.html` — use `url_for()` in the form action.
- `static/css/style.css` — styles for the flash message block (use existing CSS
  variables; reuse `.auth-error` pattern where possible).
- `CLAUDE.md` — flip the `/logout` row from "Stub — Step 3" to implemented.

## Files to create
No new files.

## New dependencies
No new dependencies. `flask` and `werkzeug` (for `check_password_hash`) are
already in `requirements.txt`.

## Rules for implementation
- No SQLAlchemy or ORMs — raw `sqlite3` via `get_db()` only.
- Parameterised queries only (`?` placeholders) — never f-strings in SQL.
- Passwords verified with `werkzeug.security.check_password_hash` — never
  compare plaintext, never re-hash for comparison.
- DB access (`get_user_by_email`) lives in `database/db.py`, never inline in the
  route.
- Use CSS variables — never hardcode hex values.
- All templates extend `base.html`; every internal link uses `url_for()`.
- Use the same generic error message for "no such user" and "wrong password"
  (e.g. "Invalid email or password") — do not reveal which field was wrong.
- `app.secret_key` must be set before `session` is used.
- The `login` view handles both `GET` (render form) and `POST` (authenticate)
  in one function via `methods=["GET", "POST"]`.
- Logout uses `session.clear()` (or pops `user_id`) and redirects — it must not
  error when no one is logged in.

## Definition of done
- [ ] Visiting `/login` shows the login form (unchanged GET behavior).
- [ ] Submitting valid credentials (e.g. `demo@spendly.com` / `demo123`) sets
      `session['user_id']` and redirects away from the login page.
- [ ] Submitting a wrong password re-renders `login.html` with a generic
      "Invalid email or password" error and does **not** log in.
- [ ] Submitting an unknown email shows the same generic error (no account
      enumeration).
- [ ] After login, the nav in `base.html` shows the logged-in state (user +
      logout link) instead of "Sign in / Get started".
- [ ] Visiting `/logout` clears the session and redirects to the landing page;
      the nav reverts to the logged-out links.
- [ ] Visiting `/logout` while not logged in redirects without error.
- [ ] No plaintext password comparison anywhere; `check_password_hash` is used.
- [ ] All new SQL uses parameterised queries; no DB logic sits inside the route.
- [ ] App still runs on port 5001 with `python app.py`.
