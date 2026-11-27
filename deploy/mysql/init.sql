-- One-time MySQL 5.6 setup. Run as an admin user:
--   mysql -u root -p < deploy/mysql/init.sql
-- Change the database name, user and password first.

CREATE DATABASE IF NOT EXISTS appdb
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

-- Use 'localhost' if MySQL is on the same machine as the app.
CREATE USER 'appuser'@'localhost' IDENTIFIED BY 'CHANGE_ME_STRONG_PASSWORD';

-- Least privilege: enough for the app and for running migrations.
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, INDEX, DROP, REFERENCES
  ON appdb.* TO 'appuser'@'localhost';

FLUSH PRIVILEGES;

-- Recommended server settings for MySQL 5.6 (my.cnf / my.ini, [mysqld]):
--   character-set-server = utf8mb4
--   collation-server     = utf8mb4_unicode_ci
--   default-storage-engine = InnoDB
--   sql_mode = STRICT_TRANS_TABLES,NO_ZERO_DATE,NO_ENGINE_SUBSTITUTION
--   innodb_file_per_table = 1
--
-- Reminder: on 5.6, indexed VARCHAR columns must be <= 191 chars with utf8mb4
-- (see app/models/base.py INDEXED_STRING_MAX).
