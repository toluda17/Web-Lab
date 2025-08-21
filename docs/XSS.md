# Cross-Site Scripting (XSS)

## Description
Cross-Site Scripting (XSS) is a vulnerability that allows attackers to inject malicious scripts into web applications.  
When the application displays user-supplied input without proper sanitization or escaping, an attacker can execute arbitrary JavaScript in the victim's browser.

In our vulnerable web app, the `bio` field in the `users` table is displayed directly on the profile page without escaping, making it a candidate for XSS.

---

## Exploit Steps
1. Register or log in as a normal user.
2. Go to the profile page (or wherever user data is displayed).
3. Update the `bio` field in the database with a malicious payload, for example:

   ```html
   <script>alert("XSS Exploit!")</script>
