# Community app

A small community board built with **Angular** (frontend), **Django** (backend) and **MySQL/MariaDB** (database, from XAMPP).

- People **register** and wait for an **admin to approve** them.
- Approved users **log in**, **write posts** and **comment**.
- New posts and comments are **pending** until an admin approves them. Only approved ones are visible to others.
- Users can **edit and delete** their own writing. Editing sends it back for approval.
- Admins use the **Admin panel** to approve or reject users, posts and comments, block or unblock users, and see a log of every action.

The code is written to be easy to read and change. Most files start with a comment that says what they do.

---

## 1. What's in the folder

```
angular-django/
├── database/
│   └── community_db.sql      all tables, views and sample data (import this first)
├── backend/                   Django REST API  (http://127.0.0.1:8000/api/)
│   ├── config/                settings, main URL list, MariaDB 10.4 fix
│   ├── accounts/              users: register, login, profile
│   ├── community/             categories, posts, comments
│   └── moderation/            admin-only: approve / reject / block
└── frontend/                  Angular app  (http://localhost:4200)
    └── src/app/
        ├── models.ts          shapes of the data (User, Post, Comment…)
        ├── services/          one file per part of the API
        ├── pages/             one folder per screen
        ├── navbar/            the top bar
        └── status-badge/      the coloured "Pending / Approved…" label
```

## 2. You need

- **XAMPP** with MySQL (MariaDB). Tested with MariaDB 10.4.32.
- **Python 3.10+**. Tested with 3.14.
- **Node.js 20+**. Tested with 24.

## 3. Set up (first time only)

### Step 1: database

1. Open the XAMPP Control Panel and press **Start** next to **MySQL** (and **Apache** if you want phpMyAdmin).
2. Import the SQL file, either:
   - **phpMyAdmin** → http://localhost/phpmyadmin → *Import* → choose `database/community_db.sql` → *Go*
   - **or** in a terminal:

```bash
D:\Software_DEV\xampp\mysql\bin\mysql.exe -u root < database/community_db.sql
```

This creates the `community_db` database with sample users, posts and comments.
You can import it again any time to get a fresh copy. **That deletes anything you added.**

### Step 2: backend (Django)

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
```

`migrate` only adds Django's own small helper tables. The app tables come from the SQL file.

If your MySQL user has a password, or the database has a different name, copy `backend/.env.example` to `backend/.env` and change the values.

### Step 3: frontend (Angular)

```bash
cd frontend
npm install
```

## 4. Run it (every time)

Use two terminals.

**Terminal 1, backend:**

```bash
cd backend
venv\Scripts\activate
python manage.py runserver
```

**Terminal 2, frontend:**

```bash
cd frontend
npm start
```

Open **http://localhost:4200**.

### Sample logins

| Username | Password    | What it shows                       |
|----------|-------------|-------------------------------------|
| `admin`  | `Admin@123` | admin: sees the **Admin** menu      |
| `sara`   | `User@123`  | normal approved user                |
| `john`   | `User@123`  | normal approved user                |
| `maria`  | `User@123`  | pending: login says "waiting for approval" |
| `tom`    | `User@123`  | blocked: cannot log in              |

To change a password:

```bash
python manage.py changepassword sara
```

To make a brand-new admin:

```bash
python manage.py createsuperuser
```

## 5. How it works (short tour)

### The approval rules
| Who writes it | Starts as   | Who can see it                   |
|---------------|-------------|----------------------------------|
| normal user   | `pending`   | the author and admins            |
| admin         | `approved`  | everyone                         |
| after an edit by a normal user | `pending` again | the author and admins |

These rules live in **`backend/community/views.py`** (top of the file).

### Login (JWT)
1. `POST /api/auth/login/` checks the password and the user's status, then returns two tokens.
2. Angular saves them in `localStorage` (`frontend/src/app/services/auth.service.ts`).
3. `frontend/src/app/auth.interceptor.ts` adds `Authorization: Bearer <token>` to every request.
4. The access token lasts **60 minutes**. When it expires, the interceptor gets a new one with the refresh token (valid **7 days**) without the user noticing.
5. If an admin blocks a user, their token stops working right away.

Token lifetimes are set in `backend/config/settings.py` → `SIMPLE_JWT`.

### Where to change things

| I want to… | Edit |
|---|---|
| change a rule (who sees what) | `backend/community/views.py` |
| add/remove an admin action | `backend/moderation/views.py` + `frontend/src/app/pages/admin/` |
| change a page's look | that page's `.html` file in `frontend/src/app/pages/` (Bootstrap classes) |
| change global colours/styles | `frontend/src/styles.css` |
| change the API address | `frontend/src/environments/environment.ts` |
| change database login | `backend/.env` (copy from `.env.example`) |
| add a category | `INSERT INTO categories …` (see the SQL file) |
| add a page | create it in `frontend/src/app/pages/`, add a line in `app.routes.ts` |

### API list
| Method | URL | Who |
|---|---|---|
| POST | `/api/auth/register/` | anyone |
| POST | `/api/auth/login/` | anyone |
| POST | `/api/auth/refresh/` | anyone |
| GET, PUT | `/api/auth/me/` | logged in |
| GET | `/api/categories/` | logged in |
| GET, POST | `/api/posts/` (`?category=<id>`, `?mine=1`) | logged in |
| GET, PUT, DELETE | `/api/posts/<id>/` | author or admin (to change) |
| GET, POST | `/api/posts/<id>/comments/` | logged in |
| PUT, DELETE | `/api/comments/<id>/` | author or admin |
| GET | `/api/admin/stats/` | admin |
| GET | `/api/admin/users/` · `/posts/` · `/comments/` (`?status=pending`) | admin |
| POST | `/api/admin/users/<id>/approve\|reject\|block\|unblock/` | admin |
| POST | `/api/admin/posts/<id>/approve\|reject/` (body: `{"reason": "…"}`) | admin |
| POST | `/api/admin/comments/<id>/approve\|reject/` | admin |
| GET | `/api/admin/logs/` | admin |

## 6. Example: add a new field

Say you want users to have a **location**. The path is always the same:
**SQL → model → serializer → Angular model → form.**

1. **Database.** Run once in phpMyAdmin (and add the column to `CREATE TABLE users` in the SQL file too):
   ```sql
   ALTER TABLE users ADD COLUMN location VARCHAR(100) NOT NULL DEFAULT '' AFTER bio;
   ```
2. **Django model.** In `backend/accounts/models.py`, under `bio`:
   ```python
   location = models.CharField(max_length=100, blank=True, default="")
   ```
   No migration needed: the SQL file owns the tables (`managed = False`).
3. **Serializer.** In `backend/accounts/serializers.py`, add `"location"` to the `fields` list of
   `UserSerializer` (to send it) and `ProfileSerializer` (to allow editing it).
4. **Angular model.** In `frontend/src/app/models.ts`, add `location: string;` to `User` and `ProfileData`.
5. **Form.** In `frontend/src/app/pages/profile/`:
   - `profile.ts`: add `location: this.auth.user()?.location ?? ''` to `form`
   - `profile.html`: copy the "Full name" block and change `full_name` to `location`

Done. Restart nothing: both servers reload on their own.

## 7. Tests

```bash
cd backend
venv\Scripts\activate
python manage.py test
```

The tests use a temporary database (`test_community_db`) that is deleted afterwards. Your data is not touched.

## 8. Good to know

- **MariaDB 10.4:** Django 5.2 officially needs MariaDB 10.5+. `backend/config/mariadb104.py` makes 10.4 work.
  If you upgrade MariaDB (or use MySQL 8), delete that file and its import in `backend/config/__init__.py`.
- **"Cannot reach the server"** in the app means the Django backend isn't running on port 8000.
- **CORS error** in the browser console: the frontend address must be listed in `FRONTEND_URLS` (`.env`) or in `CORS_ALLOWED_ORIGINS` (`settings.py`).
- **Before going live:** set a real `SECRET_KEY`, `DEBUG=False`, a MySQL password, and serve over HTTPS.
