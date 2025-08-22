## Vulnerable Route

The /login route implements authentication without password hashing or rate limiting, making it vulnerable:

# Vulnerable mode (SECURE_MODE=False)

Passwords are stored in plain text.
No account lockout or throttling.
Attackers can easily guess or brute-force credentials.

# Exploit Steps

Register a victim account in your app:

Username: victim
Password: password123

Inspect database to see plain-text password:

sqlite> SELECT * FROM users;

Password appears as password123.
Attempt login as victim with any SQL injection (if SQLi is enabled) or brute-force:

e.g., admin' OR '1'='1 bypasses login if SQLi vulnerable.

# Result:

Attacker can login without knowing the real password.
Plain-text passwords can be stolen directly from the database.

# Secure Fix
1. Enable SECURE_MODE=True
SECURE_MODE = True

2. Use password hashing
from werkzeug.security import generate_password_hash, check_password_hash

# Register route
hashed_pw = generate_password_hash(password)
conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_pw))

# Login route
user = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
if user and check_password_hash(user["password"], password):
    session["user_id"] = user["id"]


Passwords are stored securely in hashed form.
Brute-force or SQLi attacks cannot reveal actual passwords.

3. Optional Enhancements

Implement rate limiting to prevent brute-force attacks.

Lock accounts after multiple failed login attempts.

Use multi-factor authentication for sensitive accounts.