# Spec: Registration

## Overview
This feature turns the existing `/register` page from a static form into a
working account-creation flow. It adds a `POST /register` handler that
validates the submitted name, email, and password, hashes the password with
werkzeug, and persists a new row in the `users` table via a dedicated DB
helper. It exists at this stage of the Spendly roadmap (Step 2) because every
later feature — login, profile, and expense tracking — depends on real user
accounts existing in the database. Registration is the first feature that
writes user-supplied data, so it establishes the validation and
password-hashing conventions the rest of the auth flow will reuse.

## Depends on
- **Step 1 — Database setup** (complete): requires the `users` table,
  `get_db()`, and `init_db()` from `database/db.py`.

## Routes
- `GET /register` — render the registration form (already implemented; keep) — public
- `POST /register` — validate input, create the user, redirect to `/login` on success or re-render with an error — public

The existing `register()` function in `app.py` must be extended to accept both
`GET` and `POST` (`@app.route("/register", methods=["GET", "POST"])`).

## Database changes
No schema changes. The `users` table from Step 1 already has every column
needed (`id`, `name`, `email`, `password_hash`, `created_at`). This feature
adds two **query helpers** to `database/db.py` (no new tables/columns):

- `get_user_by_email(email)` — return the user row for an email, or `None`.
- `create_user(name, email, password)` — hash the password with
  `generate_password_hash`, insert the row, and return the new user id.

## Templates
- **Create:** none.
- **Modify:** `templates/register.html`
  - Change the form `action` from the hardcoded `/register` to
    `{{ url_for('register') }}` (CLAUDE.md forbids hardcoded URLs).
  - The existing `{% if error %}` block and `name`/`email`/`password` fields are
    already present and correct — re-use them as-is for error display and
    repopulation.

## Files to change
- `app.py` — extend `register()` to handle `POST`: read form fields, validate,
  call `create_user()`, redirect on success, re-render with `error` on failure.
  Add `request`, `redirect`, `url_for` to the `flask` import.
- `database/db.py` — add `get_user_by_email()` and `create_user()`.
- `templates/register.html` — swap the hardcoded form action for `url_for()`.

## Files to create
- None.

## New dependencies
No new dependencies. `werkzeug.security.generate_password_hash` is already
imported in `database/db.py` and `flask` is already a dependency.

## Rules for implementation
- No SQLAlchemy or ORMs — raw `sqlite3` via `get_db()` only.
- Parameterised queries only — `?` placeholders, never f-strings/format in SQL.
- Passwords hashed with werkzeug (`generate_password_hash`) — never store plaintext.
- Use CSS variables — never hardcode hex values (no new CSS expected; if any
  styling is added, use the existing variables in `style.css`).
- All templates extend `base.html`.
- DB logic lives in `database/db.py` only — routes must not contain inline SQL.
- Route function keeps one responsibility: validate → delegate to DB → respond.
- Use `url_for()` for every internal link/redirect — no hardcoded paths.
- Validation rules (server-side, in the route):
  - All three fields (`name`, `email`, `password`) required and non-empty after `strip()`.
  - Password minimum length 8 (matches the template's "Min. 8 characters" hint).
  - Reject duplicate emails: check `get_user_by_email()` first and show a
    friendly error rather than letting the `UNIQUE` constraint raise.
- On success, redirect to the login page (`url_for('login')`), do not auto-login
  (sessions arrive in a later step).

## Definition of done
- [ ] Visiting `GET /register` still renders the form with no errors.
- [ ] Submitting valid name/email/password creates exactly one new row in
      `users` with a hashed (non-plaintext) `password_hash`, then redirects to `/login`.
- [ ] Submitting an email that already exists re-renders the form with a visible
      error message and does **not** create a duplicate row.
- [ ] Submitting with any blank field re-renders the form with an error and
      creates no row.
- [ ] Submitting a password shorter than 8 characters re-renders the form with
      an error and creates no row.
- [ ] The stored `password_hash` verifies against the submitted password via
      `werkzeug.security.check_password_hash`.
- [ ] `register.html` uses `{{ url_for('register') }}` for the form action — no
      hardcoded URL remains.
- [ ] App starts on port 5001 without errors.
