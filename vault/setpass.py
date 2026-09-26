#!/usr/bin/env python3
"""Change the vault password.

    python3 vault/setpass.py "new password"

It rewrites KEY in vault/index.html and renames the secret folder so that
the gallery URL changes too. Passwords are case-insensitive (lowercased)
and trimmed, exactly like the gate does it.
"""
import hashlib, os, re, sys

here = os.path.dirname(os.path.abspath(__file__))
if len(sys.argv) < 2:
    sys.exit(__doc__)
pw = sys.argv[1].strip().lower()
key = hashlib.sha256(pw.encode()).hexdigest()
folder = hashlib.sha256(("door:" + pw).encode()).hexdigest()[:16]

gate = os.path.join(here, "index.html")
src = open(gate, encoding="utf-8").read()
new, n = re.subn(r'var KEY\s*=\s*"[0-9a-f]{64}"', 'var KEY  = "%s"' % key, src)
if n != 1:
    sys.exit("could not find KEY in index.html")

old = [d for d in os.listdir(here) if re.fullmatch(r"[0-9a-f]{16}", d) and os.path.isdir(os.path.join(here, d))]
if len(old) != 1:
    sys.exit("expected exactly one 16-hex secret folder in vault/, found: %r" % old)
if old[0] != folder:
    os.rename(os.path.join(here, old[0]), os.path.join(here, folder))
open(gate, "w", encoding="utf-8").write(new)
print("password set. gallery now lives at vault/%s/" % folder)
