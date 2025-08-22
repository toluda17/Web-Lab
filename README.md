# Vulnerable Web Lab

A deliberately vulnerable web application built in Flask to demonstrate common web security vulnerabilities and their mitigations.

---

## Features / Vulnerabilities Implemented

| Module | Route | Exploit | Secure Fix |
|--------|-------|---------|------------|
| SQL Injection (SQLi) | `/login` | Bypass login using raw SQL input (`admin' OR '1'='1`) | Parameterized queries |
| Cross-Site Scripting (XSS) | `/profile` | Inject `<script>alert('XSS')</script>` into bio | Escape user input before rendering |
| Cross-Site Request Forgery (CSRF) | `/change_password` | Hidden form auto-submits to change password | CSRF token via Flask-WTF |
| File Upload Vulnerability | `/upload` | Upload any file (potentially malicious) | Restrict file types, secure filenames |
| Broken Authentication | `/login` | Weak login with no rate-limiting or password hashing | Not implemented (for demonstration) |

> Toggle `SECURE_MODE` in `app.py` to switch between vulnerable and patched states.

---

## Setup Instructions

### 1. Clone the repository
```bash
git clone <https://github.com/toluda17/Web-Lab.git>
cd vuln-web-lab
```
### 2. Set up the virtual environment
```bash
# Linux/Mac
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```
### 3. Install dependencies
```bash
pip install -r requirements.txt
```
### 4. Run the application
```bash
python app/app.py
```
### 5. Access the application on a browser
```cpp
http://127.0.0.1:5000
```

## How to Test Vulnerabilities
* SQLi: Try logging in with admin' OR '1'='1 when SECURE_MODE = False.

* XSS: Update your bio with <script>alert('XSS')</script> and visit /profile.

* CSRF: While logged in, visit a malicious HTML page that auto-submits a POST to /change_password.

* File Upload: Upload files via /upload. Secure mode restricts file types.

* Broken Authentication: Weak passwords are accepted, no rate limiting (demonstration only).

## NOTE:
Flask secret key is hardcoded for demonstration purposes.

Use only in a local environment.

My project is intended for educational purposes only.
