-- auth_db keeps authentication, authorization, content-type, migration, and session data
-- separate from catalog and order business data. This is a deliberate separation-of-concerns
-- design: account/session records can be administered and secured independently.
--
-- Django version/source: Django 5.2.15 built-in auth, contenttypes, and sessions migrations,
-- compiled with this project's MySQL backend. The database is not yet present locally, so
-- this is migration-compiler DDL rather than SHOW CREATE TABLE output from a live auth_db.

CREATE DATABASE auth_db;
USE auth_db;

-- Created by Django's migration recorder before other migrations are recorded.
CREATE TABLE django_migrations (
    id BIGINT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    app VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    applied DATETIME(6) NOT NULL
) ENGINE=InnoDB;

-- django.contrib.contenttypes (final schema after contenttypes.0002).
CREATE TABLE django_content_type (
    id INTEGER AUTO_INCREMENT NOT NULL PRIMARY KEY,
    app_label VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    CONSTRAINT django_content_type_app_label_model_76bd3d3b_uniq
        UNIQUE (app_label, model)
) ENGINE=InnoDB;

-- django.contrib.auth permission and group tables.
CREATE TABLE auth_permission (
    id INTEGER AUTO_INCREMENT NOT NULL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    content_type_id INTEGER NOT NULL,
    codename VARCHAR(100) NOT NULL,
    CONSTRAINT auth_permission_content_type_id_codename_01ab375a_uniq
        UNIQUE (content_type_id, codename),
    CONSTRAINT auth_permission_content_type_id_2f476e4b_fk_django_co
        FOREIGN KEY (content_type_id) REFERENCES django_content_type (id)
) ENGINE=InnoDB;

CREATE TABLE auth_group (
    id INTEGER AUTO_INCREMENT NOT NULL PRIMARY KEY,
    name VARCHAR(150) NOT NULL UNIQUE
) ENGINE=InnoDB;

-- Django's built-in user model (django.contrib.auth.models.User).
CREATE TABLE auth_user (
    id INTEGER AUTO_INCREMENT NOT NULL PRIMARY KEY,
    password VARCHAR(128) NOT NULL,
    last_login DATETIME(6) NULL,
    is_superuser BOOL NOT NULL,
    username VARCHAR(150) NOT NULL UNIQUE,
    first_name VARCHAR(150) NOT NULL,
    last_name VARCHAR(150) NOT NULL,
    email VARCHAR(254) NOT NULL,
    is_staff BOOL NOT NULL,
    is_active BOOL NOT NULL,
    date_joined DATETIME(6) NOT NULL
) ENGINE=InnoDB;

-- Auto-created many-to-many table: auth_group.permissions.
CREATE TABLE auth_group_permissions (
    id BIGINT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    group_id INTEGER NOT NULL,
    permission_id INTEGER NOT NULL,
    CONSTRAINT auth_group_permissions_group_id_permission_id_0cd325b0_uniq
        UNIQUE (group_id, permission_id),
    CONSTRAINT auth_group_permissions_group_id_b120cbf9_fk_auth_group_id
        FOREIGN KEY (group_id) REFERENCES auth_group (id),
    CONSTRAINT auth_group_permissio_permission_id_84c5c92e_fk_auth_perm
        FOREIGN KEY (permission_id) REFERENCES auth_permission (id)
) ENGINE=InnoDB;

-- Auto-created many-to-many table: auth_user.groups.
CREATE TABLE auth_user_groups (
    id BIGINT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    group_id INTEGER NOT NULL,
    CONSTRAINT auth_user_groups_user_id_group_id_94350c0c_uniq
        UNIQUE (user_id, group_id),
    CONSTRAINT auth_user_groups_user_id_6a12ed8b_fk_auth_user_id
        FOREIGN KEY (user_id) REFERENCES auth_user (id),
    CONSTRAINT auth_user_groups_group_id_97559544_fk_auth_group_id
        FOREIGN KEY (group_id) REFERENCES auth_group (id)
) ENGINE=InnoDB;

-- Auto-created many-to-many table: auth_user.user_permissions.
CREATE TABLE auth_user_user_permissions (
    id BIGINT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    permission_id INTEGER NOT NULL,
    CONSTRAINT auth_user_user_permissions_user_id_permission_id_14a6b632_uniq
        UNIQUE (user_id, permission_id),
    CONSTRAINT auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id
        FOREIGN KEY (user_id) REFERENCES auth_user (id),
    CONSTRAINT auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm
        FOREIGN KEY (permission_id) REFERENCES auth_permission (id)
) ENGINE=InnoDB;

-- django.contrib.sessions.
CREATE TABLE django_session (
    session_key VARCHAR(40) NOT NULL PRIMARY KEY,
    session_data LONGTEXT NOT NULL,
    expire_date DATETIME(6) NOT NULL
) ENGINE=InnoDB;

CREATE INDEX django_session_expire_date_a5c62663
    ON django_session (expire_date);

-- Example signed-up user. The password value is deliberately a non-real placeholder hash.
INSERT INTO auth_user (
    password, last_login, is_superuser, username, first_name, last_name, email,
    is_staff, is_active, date_joined
) VALUES (
    'pbkdf2_sha256$600000$example-salt$not-a-real-password-hash',
    NULL, FALSE, 'student_demo', 'Demo', 'Student', 'student_demo@example.test',
    FALSE, TRUE, NOW(6)
);

-- Typical username-availability check used during signup validation.
SELECT EXISTS(
    SELECT 1
    FROM auth_user
    WHERE username = 'student_demo'
) AS username_exists;
