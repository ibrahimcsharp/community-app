-- =====================================================================
--  community_db.sql
--  Database for the "Community" app (Angular + Django + MySQL/MariaDB)
-- =====================================================================
--
--  HOW TO USE
--    1. Start XAMPP and press "Start" next to MySQL.
--    2. Import this file, either:
--         - phpMyAdmin  -> Import tab -> choose this file -> Go
--         - or a terminal:  mysql -u root < community_db.sql
--    3. Then run  `python manage.py migrate`  in the backend folder.
--       (That only adds Django's own small helper tables.)
--
--  This file is SAFE TO RE-RUN. It drops and re-creates the app tables,
--  so every run gives you a fresh copy with the sample data below.
--  WARNING: re-running deletes any data you added through the app.
--
--  WHAT IS INSIDE
--    Section 1  Database
--    Section 2  Tables   (users, categories, posts, comments, moderation_logs)
--    Section 3  Views    (ready-made queries)
--    Section 4  Sample data
--    Section 5  Useful queries to learn from (commented out)
--
--  SAMPLE LOGINS
--    admin  / Admin@123   (role: admin)
--    sara   / User@123    (approved user)
--    john   / User@123    (approved user)
--    maria  / User@123    (pending  - waiting for admin approval)
--    tom    / User@123    (blocked  - cannot log in)
--
--  STATUS VALUES USED EVERYWHERE
--    users:            pending -> approved / rejected, approved <-> blocked
--    posts, comments:  pending -> approved / rejected
--    Only "approved" rows are visible to other people.
-- =====================================================================


-- ---------------------------------------------------------------------
--  SECTION 1: DATABASE
-- ---------------------------------------------------------------------
-- utf8mb4 stores every character, including emoji.
CREATE DATABASE IF NOT EXISTS community_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE community_db;

-- Turn off foreign key checks so we can drop tables in any order.
SET FOREIGN_KEY_CHECKS = 0;

DROP VIEW  IF EXISTS v_community_feed;
DROP VIEW  IF EXISTS v_moderation_queue;
DROP VIEW  IF EXISTS v_user_stats;

DROP TABLE IF EXISTS moderation_logs;
DROP TABLE IF EXISTS comments;
DROP TABLE IF EXISTS posts;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS users;

SET FOREIGN_KEY_CHECKS = 1;


-- ---------------------------------------------------------------------
--  SECTION 2: TABLES
-- ---------------------------------------------------------------------

-- ===== users =========================================================
-- Everyone who can log in. Admins are users with role = 'admin'.
-- Django model: backend/accounts/models.py -> User
CREATE TABLE users (
    id           INT UNSIGNED  NOT NULL AUTO_INCREMENT,
    username     VARCHAR(50)   NOT NULL,                 -- used to log in
    email        VARCHAR(255)  NOT NULL,
    password     VARCHAR(128)  NOT NULL,                 -- Django password hash, never plain text
    full_name    VARCHAR(100)  NOT NULL DEFAULT '',
    bio          VARCHAR(500)  NOT NULL DEFAULT '',      -- short "about me"
    role         ENUM('user', 'admin')
                               NOT NULL DEFAULT 'user',
    status       ENUM('pending', 'approved', 'rejected', 'blocked')
                               NOT NULL DEFAULT 'pending', -- new sign-ups wait for an admin
    approved_by  INT UNSIGNED  NULL,                     -- admin who approved this user
    approved_at  DATETIME      NULL,
    last_login   DATETIME      NULL,                     -- filled in by Django on login
    created_at   DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at   DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    UNIQUE KEY uq_users_username (username),
    UNIQUE KEY uq_users_email    (email),
    KEY idx_users_status     (status),
    KEY idx_users_created_at (created_at),

    CONSTRAINT fk_users_approved_by
        FOREIGN KEY (approved_by) REFERENCES users (id)
        ON DELETE SET NULL,                              -- deleting the admin keeps the user

    CONSTRAINT chk_users_username_not_empty CHECK (CHAR_LENGTH(TRIM(username)) >= 3),
    CONSTRAINT chk_users_email_has_at       CHECK (email LIKE '%_@_%')
) ENGINE = InnoDB COMMENT = 'People who can log in (users and admins)';


-- ===== categories ====================================================
-- Topics a post can belong to. Edit the sample rows below to change them.
-- Django model: backend/community/models.py -> Category
CREATE TABLE categories (
    id           INT UNSIGNED  NOT NULL AUTO_INCREMENT,
    name         VARCHAR(50)   NOT NULL,                 -- shown in the app, e.g. "Questions"
    slug         VARCHAR(50)   NOT NULL,                 -- short url-friendly name, e.g. "questions"
    description  VARCHAR(255)  NOT NULL DEFAULT '',
    created_at   DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    UNIQUE KEY uq_categories_name (name),
    UNIQUE KEY uq_categories_slug (slug)
) ENGINE = InnoDB COMMENT = 'Post topics';


-- ===== posts =========================================================
-- What users write on the community board.
-- Django model: backend/community/models.py -> Post
CREATE TABLE posts (
    id             INT UNSIGNED  NOT NULL AUTO_INCREMENT,
    user_id        INT UNSIGNED  NOT NULL,               -- author
    category_id    INT UNSIGNED  NOT NULL,
    title          VARCHAR(200)  NOT NULL,
    body           TEXT          NOT NULL,
    status         ENUM('pending', 'approved', 'rejected')
                                 NOT NULL DEFAULT 'pending',
    reject_reason  VARCHAR(255)  NOT NULL DEFAULT '',    -- shown to the author when rejected
    reviewed_by    INT UNSIGNED  NULL,                   -- admin who approved / rejected it
    reviewed_at    DATETIME      NULL,
    created_at     DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at     DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    KEY idx_posts_user       (user_id),
    KEY idx_posts_category   (category_id),
    KEY idx_posts_status     (status),
    KEY idx_posts_created_at (created_at),
    KEY idx_posts_status_created (status, created_at),   -- speeds up "latest approved posts"

    CONSTRAINT fk_posts_user
        FOREIGN KEY (user_id) REFERENCES users (id)
        ON DELETE CASCADE,                               -- delete a user -> delete their posts
    CONSTRAINT fk_posts_category
        FOREIGN KEY (category_id) REFERENCES categories (id)
        ON DELETE RESTRICT,                              -- cannot delete a category that is in use
    CONSTRAINT fk_posts_reviewed_by
        FOREIGN KEY (reviewed_by) REFERENCES users (id)
        ON DELETE SET NULL,

    CONSTRAINT chk_posts_title_not_empty CHECK (CHAR_LENGTH(TRIM(title)) > 0),
    CONSTRAINT chk_posts_body_not_empty  CHECK (CHAR_LENGTH(TRIM(body))  > 0)
) ENGINE = InnoDB COMMENT = 'Community posts written by users';


-- ===== comments ======================================================
-- Replies under a post.
-- Django model: backend/community/models.py -> Comment
CREATE TABLE comments (
    id             INT UNSIGNED  NOT NULL AUTO_INCREMENT,
    post_id        INT UNSIGNED  NOT NULL,
    user_id        INT UNSIGNED  NOT NULL,               -- author
    body           TEXT          NOT NULL,
    status         ENUM('pending', 'approved', 'rejected')
                                 NOT NULL DEFAULT 'pending',
    reject_reason  VARCHAR(255)  NOT NULL DEFAULT '',
    reviewed_by    INT UNSIGNED  NULL,
    reviewed_at    DATETIME      NULL,
    created_at     DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at     DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    KEY idx_comments_post       (post_id),
    KEY idx_comments_user       (user_id),
    KEY idx_comments_status     (status),
    KEY idx_comments_created_at (created_at),

    CONSTRAINT fk_comments_post
        FOREIGN KEY (post_id) REFERENCES posts (id)
        ON DELETE CASCADE,                               -- delete a post -> delete its comments
    CONSTRAINT fk_comments_user
        FOREIGN KEY (user_id) REFERENCES users (id)
        ON DELETE CASCADE,
    CONSTRAINT fk_comments_reviewed_by
        FOREIGN KEY (reviewed_by) REFERENCES users (id)
        ON DELETE SET NULL,

    CONSTRAINT chk_comments_body_not_empty CHECK (CHAR_LENGTH(TRIM(body)) > 0)
) ENGINE = InnoDB COMMENT = 'Comments on posts';


-- ===== moderation_logs ===============================================
-- History of every admin action (who approved / rejected / blocked what).
-- target_type + target_id point at a row in users, posts or comments.
-- There is no foreign key on target_id because it can point at 3 tables,
-- and the log should stay even if that row is deleted later.
-- Django model: backend/community/models.py -> ModerationLog
CREATE TABLE moderation_logs (
    id           INT UNSIGNED  NOT NULL AUTO_INCREMENT,
    admin_id     INT UNSIGNED  NULL,                     -- NULL if that admin was deleted
    target_type  ENUM('user', 'post', 'comment') NOT NULL,
    target_id    INT UNSIGNED  NOT NULL,
    action       ENUM('approve', 'reject', 'block', 'unblock') NOT NULL,
    note         VARCHAR(255)  NOT NULL DEFAULT '',      -- e.g. the reject reason
    created_at   DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    KEY idx_logs_admin      (admin_id),
    KEY idx_logs_target     (target_type, target_id),
    KEY idx_logs_created_at (created_at),

    CONSTRAINT fk_logs_admin
        FOREIGN KEY (admin_id) REFERENCES users (id)
        ON DELETE SET NULL
) ENGINE = InnoDB COMMENT = 'Audit trail of admin approvals, rejections and blocks';


-- ---------------------------------------------------------------------
--  SECTION 3: VIEWS
--  A view is a saved SELECT you can query like a table.
--  The app does not need them; they are handy in phpMyAdmin.
-- ---------------------------------------------------------------------

-- What everyone sees on the community board: approved posts,
-- with author, category and number of approved comments.
CREATE VIEW v_community_feed AS
SELECT
    p.id                                   AS post_id,
    p.title,
    p.body,
    c.name                                 AS category,
    u.username                             AS author,
    p.created_at,
    (SELECT COUNT(*)
       FROM comments cm
      WHERE cm.post_id = p.id
        AND cm.status = 'approved')        AS comment_count
FROM posts p
JOIN users      u ON u.id = p.user_id
JOIN categories c ON c.id = p.category_id
WHERE p.status = 'approved'
ORDER BY p.created_at DESC;

-- Everything waiting for an admin, in one list.
CREATE VIEW v_moderation_queue AS
SELECT 'user'    AS item_type, u.id AS item_id,
       u.username AS summary, u.username AS author, u.created_at
  FROM users u
 WHERE u.status = 'pending'
UNION ALL
SELECT 'post', p.id, p.title, u.username, p.created_at
  FROM posts p JOIN users u ON u.id = p.user_id
 WHERE p.status = 'pending'
UNION ALL
SELECT 'comment', cm.id, LEFT(cm.body, 80), u.username, cm.created_at
  FROM comments cm JOIN users u ON u.id = cm.user_id
 WHERE cm.status = 'pending';

-- How active each user is.
CREATE VIEW v_user_stats AS
SELECT
    u.id,
    u.username,
    u.role,
    u.status,
    (SELECT COUNT(*) FROM posts    p  WHERE p.user_id  = u.id)                          AS total_posts,
    (SELECT COUNT(*) FROM posts    p  WHERE p.user_id  = u.id AND p.status  = 'approved') AS approved_posts,
    (SELECT COUNT(*) FROM comments cm WHERE cm.user_id = u.id)                          AS total_comments,
    (SELECT COUNT(*) FROM comments cm WHERE cm.user_id = u.id AND cm.status = 'approved') AS approved_comments
FROM users u;


-- ---------------------------------------------------------------------
--  SECTION 4: SAMPLE DATA
--  Passwords are real Django hashes:
--    admin -> Admin@123      everyone else -> User@123
--  To set a new password later, run in the backend folder:
--    python manage.py changepassword <username>
-- ---------------------------------------------------------------------

-- ===== users =====
INSERT INTO users (id, username, email, password, full_name, bio, role, status, approved_by, approved_at, created_at) VALUES
(1, 'admin', 'admin@community.local',
    'pbkdf2_sha256$1000000$6Kwl3AScR2vWhKV0k4NRM7$LyKgWNC2KPjcNEmKyICs8/KWbH78NdTSkxBlYfTo2h8=',
    'Site Admin', 'I keep the community friendly.', 'admin', 'approved', NULL, NOW() - INTERVAL 30 DAY, NOW() - INTERVAL 30 DAY),
(2, 'sara', 'sara@example.com',
    'pbkdf2_sha256$1000000$FJDWCSYC8xqUeqBD7Zrrey$RWFi0zg5eIuDbg8x11RACNiD07pH+WZhKrjwVpLxmxo=',
    'Sara Khan', 'Frontend developer who loves Angular.', 'user', 'approved', 1, NOW() - INTERVAL 20 DAY, NOW() - INTERVAL 21 DAY),
(3, 'john', 'john@example.com',
    'pbkdf2_sha256$1000000$FJDWCSYC8xqUeqBD7Zrrey$RWFi0zg5eIuDbg8x11RACNiD07pH+WZhKrjwVpLxmxo=',
    'John Smith', 'Learning Python and Django.', 'user', 'approved', 1, NOW() - INTERVAL 15 DAY, NOW() - INTERVAL 16 DAY),
(4, 'maria', 'maria@example.com',
    'pbkdf2_sha256$1000000$FJDWCSYC8xqUeqBD7Zrrey$RWFi0zg5eIuDbg8x11RACNiD07pH+WZhKrjwVpLxmxo=',
    'Maria Lopez', 'Just joined!', 'user', 'pending', NULL, NULL, NOW() - INTERVAL 1 DAY),
(5, 'tom', 'tom@example.com',
    'pbkdf2_sha256$1000000$FJDWCSYC8xqUeqBD7Zrrey$RWFi0zg5eIuDbg8x11RACNiD07pH+WZhKrjwVpLxmxo=',
    'Tom Brown', '', 'user', 'blocked', 1, NOW() - INTERVAL 10 DAY, NOW() - INTERVAL 12 DAY);

-- ===== categories =====
INSERT INTO categories (id, name, slug, description) VALUES
(1, 'General',   'general',   'Anything about the community'),
(2, 'Questions', 'questions', 'Ask for help or advice'),
(3, 'News',      'news',      'Announcements and updates'),
(4, 'Off-topic', 'off-topic', 'Everything else');

-- ===== posts =====
INSERT INTO posts (id, user_id, category_id, title, body, status, reject_reason, reviewed_by, reviewed_at, created_at) VALUES
(1, 1, 3, 'Welcome and community rules',
    'Welcome! Be kind, stay on topic and do not post adverts. New posts and comments are checked by an admin before they appear.',
    'approved', '', 1, NOW() - INTERVAL 29 DAY, NOW() - INTERVAL 29 DAY),
(2, 2, 1, 'Hello from Sara',
    'Hi everyone, I build web apps with Angular. Happy to help with frontend questions.',
    'approved', '', 1, NOW() - INTERVAL 19 DAY, NOW() - INTERVAL 19 DAY),
(3, 3, 2, 'How do I learn Django quickly?',
    'I know basic Python. What is the fastest way to get comfortable with Django and Django REST Framework?',
    'approved', '', 1, NOW() - INTERVAL 14 DAY, NOW() - INTERVAL 14 DAY),
(4, 2, 4, 'Favourite books this year',
    'Share the best book you read this year. Mine is a novel about a lighthouse keeper.',
    'pending', '', NULL, NULL, NOW() - INTERVAL 2 HOUR),
(5, 3, 1, 'BUY CHEAP WATCHES!!!',
    'Best prices, visit my shop now!!!',
    'rejected', 'Advertising is not allowed.', 1, NOW() - INTERVAL 5 DAY, NOW() - INTERVAL 6 DAY),
(6, 5, 4, 'Spam spam spam',
    'Click this link to win a prize.',
    'rejected', 'Spam.', 1, NOW() - INTERVAL 11 DAY, NOW() - INTERVAL 11 DAY);

-- ===== comments =====
INSERT INTO comments (id, post_id, user_id, body, status, reject_reason, reviewed_by, reviewed_at, created_at) VALUES
(1, 1, 2, 'Thanks for setting this up!',                                   'approved', '', 1, NOW() - INTERVAL 18 DAY, NOW() - INTERVAL 18 DAY),
(2, 1, 3, 'Happy to be here.',                                             'approved', '', 1, NOW() - INTERVAL 13 DAY, NOW() - INTERVAL 13 DAY),
(3, 3, 2, 'Start with the official Django tutorial, then the DRF quickstart.', 'approved', '', 1, NOW() - INTERVAL 12 DAY, NOW() - INTERVAL 12 DAY),
(4, 3, 1, 'Also build a tiny project of your own as soon as you can.',     'approved', '', 1, NOW() - INTERVAL 12 DAY, NOW() - INTERVAL 12 DAY),
(5, 2, 3, 'Welcome Sara! I might ask you about Angular routing.',          'pending',  '', NULL, NULL, NOW() - INTERVAL 3 HOUR),
(6, 2, 5, 'Visit my site for free stuff',                                  'rejected', 'Spam.', 1, NOW() - INTERVAL 11 DAY, NOW() - INTERVAL 11 DAY);

-- ===== moderation_logs (matches the data above) =====
INSERT INTO moderation_logs (admin_id, target_type, target_id, action, note, created_at) VALUES
(1, 'user',    2, 'approve', '',                            NOW() - INTERVAL 20 DAY),
(1, 'user',    3, 'approve', '',                            NOW() - INTERVAL 15 DAY),
(1, 'user',    5, 'approve', '',                            NOW() - INTERVAL 11 DAY),
(1, 'post',    6, 'reject',  'Spam.',                       NOW() - INTERVAL 11 DAY),
(1, 'comment', 6, 'reject',  'Spam.',                       NOW() - INTERVAL 11 DAY),
(1, 'user',    5, 'block',   'Posting spam.',               NOW() - INTERVAL 10 DAY),
(1, 'post',    5, 'reject',  'Advertising is not allowed.', NOW() - INTERVAL 5 DAY);


-- ---------------------------------------------------------------------
--  SECTION 5: USEFUL QUERIES (remove the "-- " to run one)
-- ---------------------------------------------------------------------

-- Everything waiting for approval:
-- SELECT * FROM v_moderation_queue ORDER BY created_at;

-- The public community board:
-- SELECT * FROM v_community_feed;

-- Make an existing user an admin:
-- UPDATE users SET role = 'admin', status = 'approved' WHERE username = 'sara';

-- Approve every pending user at once:
-- UPDATE users SET status = 'approved', approved_by = 1, approved_at = NOW() WHERE status = 'pending';

-- Posts per category:
-- SELECT c.name, COUNT(p.id) AS posts
--   FROM categories c LEFT JOIN posts p ON p.category_id = c.id
--  GROUP BY c.id ORDER BY posts DESC;

-- Last 20 admin actions with the admin's name:
-- SELECT l.created_at, u.username AS admin, l.action, l.target_type, l.target_id, l.note
--   FROM moderation_logs l LEFT JOIN users u ON u.id = l.admin_id
--  ORDER BY l.created_at DESC LIMIT 20;

-- Most active users:
-- SELECT * FROM v_user_stats ORDER BY approved_posts + approved_comments DESC;
