## Vulnerable Route

The /upload route allows users to upload files with no restrictions.
It saves the file with its original filename directly to the /uploads directory:

## Exploit Steps

Victim visits /upload and uploads a file.

Attacker uploads a malicious file, e.g. shell.py containing:

import os
os.system("whoami")


or 'evil.html' containing:

<script>alert('XSS');</script>


The file is stored in /uploads with no filtering.

If the server is misconfigured to serve files from /uploads/ (common in real apps), the attacker could execute malicious code or deliver phishing pages from the trusted domain.

## Impact:

* Remote Code Execution (if script is run on server).

* XSS or phishing (if attacker serves HTML/JS).

* Arbitrary file overwrite (e.g., attacker uploads app.py).

## Secure Fix

To mitigate file upload vulnerabilities:

Restrict allowed file types (e.g., only .png, .jpg, .txt).
Rename uploaded files using secure_filename() or UUIDs.
Store files in a non-executable directory (not served directly by Flask).