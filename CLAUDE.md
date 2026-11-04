# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A community board: users register (pending until an admin approves), write posts and comments (pending until approved), and admins moderate everything from an Angular admin panel. Angular 22 + Bootstrap frontend, Django 5.2 + DRF + simplejwt backend, MariaDB 10.4 from XAMPP (`D:\Software_DEV\xampp`).

**Main goal of the code: easy for a beginner to read and edit.** Keep that style: short function views with a docstring, plain string statuses (`"pending"`, `"approved"`…) that match the SQL ENUMs, a top-of-file comment saying what each file does, no ViewSets/routers, no clever abstractions.

## Commands

Backend (run from `backend/`, venv at `backend/venv`):

```bash
venv\Scripts\python.exe manage.py runserver            # API on http://127.0.0.1:8000/api/
venv\Scripts\python.exe manage.py test                 # all tests
venv\Scripts\python.exe manage.py test community.tests.CommunityTests.test_comment_flow   # one test
venv\Scripts\python.exe manage.py migrate              # only Django's internal tables (auth, contenttypes)
```

Frontend (run from `frontend/`):

```bash
npm start          # ng serve on http://localhost:4200
npx ng build       # must build with no errors
```

No frontend unit tests (project was generated with `--skip-tests`). Prettier config: `frontend/.prettierrc` (width 100, single quotes).

Database (reset to clean sample data; also drops anything added through the app):

```bash
D:\Software_DEV\xampp\mysql\bin\mysql.exe -u root < database/community_db.sql
```

`.claude/launch.json` has `backend` and `frontend` configs for the preview browser. Sample logins: `admin`/`Admin@123`, `sara` and `john`/`User@123` (approved), `maria` (pending), `tom` (blocked).

## Architecture: things that span several files

**The SQL file owns the schema.** `database/community_db.sql` creates every app table. All Django models are `managed = False` with explicit `db_table`, and the `accounts`/`community` apps have **no migrations folders** on purpose. Adding a column = edit the SQL `CREATE TABLE` (+ an `ALTER TABLE` for existing DBs) → model field → serializer `fields` → `frontend/src/app/models.ts` → the form. Never run `makemigrations` for these apps.

**Tests still work despite `managed = False`** because `config/test_runner.py` (set as `TEST_RUNNER`) flips every model to managed before the test DB is built, and switches to the MD5 hasher for speed. Test DB tables come from the models, so they lack the SQL file's CHECK constraints and ENUMs.

**MariaDB 10.4 workaround.** `config/__init__.py` installs PyMySQL as `MySQLdb` and imports `config/mariadb104.py`, which patches Django's MySQL `DatabaseFeatures`: lowers the minimum version to 10.4 and sets `can_return_columns_from_insert = False` (10.4 has no `INSERT … RETURNING`; without this every insert fails). Delete both if MariaDB is upgraded to 10.5+.

**Approval model.** Custom user `accounts.User` (`AbstractBaseUser`, `AUTH_USER_MODEL`) has `is_active` = `status == "approved"`, so simplejwt rejects tokens of pending/blocked users automatically, and blocking takes effect immediately. Login (`accounts/views.py`) checks the password manually so it can return a specific message per status. Visibility rules live at the top of `community/views.py`:
- `approved_or_mine(user)` is the feed filter (same for admins).
- `visible_to(user)` is for opening one post and its comments, and admins see everything.
- `starting_status()` auto-approves admin writing and resets non-admin edits to `pending`.

Every admin action in `moderation/views.py` writes a `moderation_logs` row via `write_log()`.

**Ordering gotcha:** Django drops `Meta.ordering` on queries with `Count()`/GROUP BY, so `posts_with_comment_count()` sets `order_by` explicitly. Do the same for any new annotated query.

**Times:** `USE_TZ = False`, so naive local times match MySQL's `NOW()` in the seed data.

**Frontend flow.**
- `AuthService` keeps the user in a signal (restored from `localStorage`) plus the access/refresh tokens.
- `auth.interceptor.ts` adds the Bearer header. On a 401 it refreshes once and retries, and logs out with `?reason=expired` if that fails.
- `guards.ts` only protects screens, since the real checks are in Django.
- The router uses `withComponentInputBinding()`, so route params and query params (`:id`, `?reason=`) arrive as component `input()`s.

**Zoneless Angular:** page state must live in signals. Form models are plain objects bound with `ngModel`, and they re-render because a signal changes in the same callback. If you change only a plain property inside an async callback, the screen won't update.

`PostForm` is used both as a routed page (`/posts/new`, `/posts/:id/edit`) and embedded in the community page (`[embedded]="true"`, emits `saved`/`cancelled`). API errors become one sentence via `error-message.ts`. The API base URL lives only in `src/environments/environment.ts`.

## Repo / git

This folder sits inside the larger `D:\Software_DEV` git repo, which holds many unrelated projects. Stage only paths under `Claude-Code/angular-django`. Work for this app is on branch `community-app`.

**Publishing.** This folder alone is published to the **public** repo `ibrahimcsharp/community-app` (remote `community-app` in the parent repo) with a subtree split, run from `D:\Software_DEV`:

```bash
git push community-app $(git subtree split --prefix=Claude-Code/angular-django community-app):refs/heads/main
```

Because the repo is public, make sure no `backend/.env` or real keys are tracked before pushing.

`.claude/settings.json` denies `makemigrations` and any read or edit of `backend/.env`, and asks before `git push` or anything touching `community_db.sql`.
