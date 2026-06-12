#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/common.sh"
load_env
require_cmd python3

admin_user="${EXOCORTEX_ADMIN_USERNAME:-admin}"
admin_password="${EXOCORTEX_ADMIN_PASSWORD:-}"
profiles_csv="${EXOCORTEX_ALLOWED_PROFILES:-default,manut}"
default_profile="${EXOCORTEX_DEFAULT_PROFILE:-default}"
db_path="$EXOCORTEX_WEB_UI_HOME/hermes-web-ui.db"

[ -n "$admin_password" ] || fail "EXOCORTEX_ADMIN_PASSWORD não definido"
mkdir -p "$EXOCORTEX_WEB_UI_HOME"

python3 - "$db_path" "$admin_user" "$admin_password" "$profiles_csv" "$default_profile" <<'PY'
import hashlib
import json
import secrets
import sqlite3
import sys
import time
from pathlib import Path

_, db_path, username, password, profiles_csv, default_profile = sys.argv
profiles = [p.strip() for p in profiles_csv.split(',') if p.strip()]
if not profiles:
    profiles = ['default']
if default_profile not in profiles:
    profiles.insert(0, default_profile)

path = Path(db_path)
path.parent.mkdir(parents=True, exist_ok=True)
conn = sqlite3.connect(path)
cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  role TEXT NOT NULL DEFAULT 'admin',
  status TEXT NOT NULL DEFAULT 'active',
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL,
  last_login_at INTEGER,
  avatar TEXT NOT NULL DEFAULT ''
)
""")
cur.execute("""
CREATE TABLE IF NOT EXISTS user_profiles (
  user_id INTEGER NOT NULL,
  profile_name TEXT NOT NULL DEFAULT 'default',
  is_default INTEGER NOT NULL DEFAULT 0,
  created_at INTEGER NOT NULL
)
""")
cur.execute("CREATE INDEX IF NOT EXISTS idx_user_profiles_user ON user_profiles(user_id)")
cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_user_profiles_default ON user_profiles(user_id) WHERE is_default = 1")

salt = secrets.token_hex(16)
password_hash = 'scrypt:%s:%s' % (
    salt,
    hashlib.scrypt(password.encode('utf-8'), salt=salt.encode('utf-8'), n=16384, r=8, p=1, dklen=64).hex(),
)
now = int(time.time() * 1000)
row = cur.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
if row:
    user_id = int(row[0])
    cur.execute(
        "UPDATE users SET password_hash = ?, role = 'super_admin', status = 'active', updated_at = ? WHERE id = ?",
        (password_hash, now, user_id),
    )
else:
    first = cur.execute("SELECT id FROM users ORDER BY id ASC LIMIT 1").fetchone()
    if first:
        user_id = int(first[0])
        cur.execute(
            "UPDATE users SET username = ?, password_hash = ?, role = 'super_admin', status = 'active', updated_at = ? WHERE id = ?",
            (username, password_hash, now, user_id),
        )
    else:
        cur.execute(
            "INSERT INTO users (username, password_hash, role, status, created_at, updated_at, avatar) VALUES (?, ?, 'super_admin', 'active', ?, ?, '')",
            (username, password_hash, now, now),
        )
        user_id = int(cur.lastrowid)

cur.execute("DELETE FROM user_profiles WHERE user_id = ?", (user_id,))
for profile in profiles:
    cur.execute(
        "INSERT INTO user_profiles (user_id, profile_name, is_default, created_at) VALUES (?, ?, ?, ?)",
        (user_id, profile, 1 if profile == default_profile else 0, now),
    )

conn.commit()
summary = {
    'db_path': str(path),
    'username': username,
    'profiles': profiles,
    'default_profile': default_profile,
}
print(json.dumps(summary, ensure_ascii=False))
conn.close()
PY

log "Admin da UI bootstrapado em $db_path"
