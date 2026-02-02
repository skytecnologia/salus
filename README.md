# salus

Salus is a web application that allows health patients to manage their medical records.

# To run the application:
python -m uvicorn src.main:app --host 0.0.0.0 --port 8008 --reload --env-file conf/.env.local

# Pull from remote git
git pull origin main

# Access postgres and create database:
sudo -u postgres psql
    postgres=# CREATE USER salus WITH PASSWORD 'strong_password';
    postgres=# ALTER DATABASE template1 REFRESH COLLATION VERSION;
    postgres=# CREATE DATABASE salus WITH OWNER salus ENCODING 'UTF8';
    postgres=# \q

# Access salus database using postgres user:
sudo -u postgres psql salus

# Usefull commands to grant previligies to 3rd users on salus database:
#   if tables already exists:
\c salus
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO remote_user;
#   grant future tables privileges:
\c salus
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO remote_user;
