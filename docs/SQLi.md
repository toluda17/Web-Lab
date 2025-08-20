# SQL Injection (SQLi)

## Vulnerability Description
The `/login` route directly concatenates user input into a SQL query when `SECURE_MODE=False`.  
This allows attackers to manipulate the query and bypass authentication.

---

## Exploit Steps

1. Go to the login page (`/login`).
2. Enter the following credentials:
   - **Username:** `admin' OR '1'='1`  
   - **Password:** anything (e.g., `test`)
3. The resulting SQL query looks like this:
   ```sql
   SELECT * FROM users WHERE username='admin' OR '1'='1' AND password='test'
