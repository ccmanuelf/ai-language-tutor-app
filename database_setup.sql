-- AI Language Tutor App - Database Setup Script
-- Creates database, user, and sets proper permissions

-- Create the database
CREATE DATABASE IF NOT EXISTS ai_language_tutor
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

-- Create the application user
CREATE USER IF NOT EXISTS 'ai_tutor_user'@'localhost' IDENTIFIED BY 'ai_tutor_pass_2024';

-- Grant privileges to the application user
GRANT ALL PRIVILEGES ON ai_language_tutor.* TO 'ai_tutor_user'@'localhost';

-- Also grant the user ability to create test databases
GRANT CREATE ON *.* TO 'ai_tutor_user'@'localhost';

-- Set root password for security
ALTER USER 'root'@'localhost' IDENTIFIED BY 'password';

-- Remove anonymous users
DELETE FROM mysql.user WHERE User='';

-- Remove remote root access (keep only localhost)
DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');

-- Remove test database
DROP DATABASE IF EXISTS test;
DELETE FROM mysql.db WHERE Db='test' OR Db='test\\_%';

-- Reload privilege tables
FLUSH PRIVILEGES;

-- Show created database
SHOW DATABASES;

-- Show users
SELECT User, Host FROM mysql.user WHERE User IN ('root', 'ai_tutor_user');

-- Confirm the database was created properly
USE ai_language_tutor;
SELECT DATABASE() as current_database, 
       @@character_set_database as charset, 
       @@collation_database as collation;