"""Durable local or Vercel storage. Every course lookup is scoped to its owner."""

from __future__ import annotations

import json
import os
import time
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from threading import RLock

import httpx


class BlobStore:
    """Small JSON document store backed by a private Vercel Blob object."""

    API_URL = "https://vercel.com/api/blob/"
    PATHNAME = "exam-radar/state.json"

    def __init__(self, token: str):
        self.token = token
        parts = token.split("_")
        if len(parts) < 4:
            raise ValueError("Invalid BLOB_READ_WRITE_TOKEN")
        self.object_url = f"https://{parts[3]}.private.blob.vercel-storage.com/{self.PATHNAME}"
        self.lock = RLock()
        self.path = Path("/tmp/exam-radar.sqlite3")

    @property
    def headers(self):
        return {"Authorization": f"Bearer {self.token}"}

    @staticmethod
    def empty_state():
        return {"users": {}, "courses": {}, "shares": {}, "comments": {}, "auth_identities": {}, "auth_sessions": {}, "oauth_states": {}, "login_events": {}, "rate_limits": {}}

    def read(self) -> tuple[dict, str | None]:
        response = httpx.get(
            self.object_url,
            headers=self.headers,
            params={"cache": "0"},
            timeout=15,
        )
        if response.status_code == 404:
            return self.empty_state(), None
        response.raise_for_status()
        state = self.empty_state()
        saved = response.json()
        if isinstance(saved, dict):
            for key in state:
                if isinstance(saved.get(key), dict):
                    state[key] = saved[key]
        etag = response.headers.get("etag", "")
        if etag.startswith('W/"') and etag.endswith('"'):
            etag = etag[3:-1]
        else:
            etag = etag.strip('"')
        return state, etag or None

    def write(self, state: dict, etag: str | None):
        headers = {
            **self.headers,
            "x-api-version": "12",
            "x-vercel-blob-access": "private",
            "x-add-random-suffix": "0",
            "x-content-type": "application/json",
        }
        if etag:
            headers["x-if-match"] = etag
            headers["x-allow-overwrite"] = "1"
        content = json.dumps(state, ensure_ascii=False, separators=(",", ":")).encode()
        for attempt in range(4):
            response = httpx.put(
                self.API_URL,
                params={"pathname": self.PATHNAME},
                headers=headers,
                content=content,
                timeout=20,
            )
            if response.status_code in {409, 412}:
                return False
            if response.status_code not in {429, 500, 502, 503, 504}:
                response.raise_for_status()
                return True
            time.sleep(.15 * (attempt + 1))
        response.raise_for_status()

    def update(self, change):
        with self.lock:
            for _ in range(8):
                state, etag = self.read()
                result = change(state)
                if self.write(state, etag):
                    return result
            raise RuntimeError("The shared data changed too quickly. Please retry.")

    def user(self, user_id: str | None):
        return self.read()[0]["users"].get(user_id) if user_id else None

    def save_user(self, user: dict):
        self.update(lambda state: state["users"].__setitem__(user["id"], user))

    def courses(self, owner: str):
        state = self.read()[0]
        return [item["payload"] for item in state["courses"].values() if item["owner"] == owner]

    def course(self, owner: str, course_id: str):
        item = self.read()[0]["courses"].get(course_id)
        return item["payload"] if item and item["owner"] == owner else None

    def save_course(self, owner: str, course: dict):
        def change(state):
            existing = state["courses"].get(course["id"])
            if existing and existing["owner"] != owner:
                raise ValueError("Course belongs to another user")
            state["courses"][course["id"]] = {"owner": owner, "payload": course}
        self.update(change)

    def create_share(self, owner: str, course_id: str, token: str, payload: dict, created_at: str):
        self.update(lambda state: state["shares"].__setitem__(token, {"owner": owner, "course_id": course_id, "payload": payload, "created_at": created_at}))

    def share(self, token: str):
        state = self.read()[0]
        item = state["shares"].get(token)
        if not item:
            return None
        comments = [comment for comment in state["comments"].values() if comment["token"] == token]
        comments.sort(key=lambda item: item["createdAt"])
        return {**item["payload"], "comments": [{key: comment[key] for key in ("id", "author", "body", "createdAt")} for comment in comments]}

    def add_comment(self, token: str, user: dict, comment: dict):
        def change(state):
            state["comments"][comment["id"]] = {**comment, "token": token, "author_id": user["id"]}
        self.update(change)

    # Authentication persistence for Vercel Blob mode.
    def auth_identity(self, provider: str, subject: str):
        state = self.read()[0]
        return next((v for v in state["auth_identities"].values() if v.get("provider") == provider and v.get("subject") == subject), None)
    def save_auth_identity(self, identity): self.update(lambda s: s["auth_identities"].__setitem__(identity["id"], identity))
    def save_auth_session(self, item): self.update(lambda s: s["auth_sessions"].__setitem__(item["id"], item))
    def auth_session(self, sid): return self.read()[0]["auth_sessions"].get(sid)
    def revoke_auth_session(self, sid): self.update(lambda s: s["auth_sessions"].get(sid, {}).update(revoked=True))
    def revoke_identity_sessions(self, identity_id): self.update(lambda s: [item.update(revoked=True) for item in s["auth_sessions"].values() if item.get("identityId") == identity_id])
    def save_oauth_state(self, item): self.update(lambda s: s["oauth_states"].__setitem__(item["state"], item))
    def pop_oauth_state(self, state):
        out = None
        def change(s):
            nonlocal out
            out = s["oauth_states"].pop(state, None)
        self.update(change); return out
    def record_login(self, event): self.update(lambda s: s["login_events"].__setitem__(event["id"], event))
    def login_stats(self):
        events = list(self.read()[0]["login_events"].values())
        return {"totalLogins": len(events), "uniqueUsers": len({e.get("identityId") for e in events}), "byProvider": {p: sum(1 for e in events if e.get("provider") == p) for p in {e.get("provider") for e in events}}}
    def rate_limit(self, key, now_ts, window):
        result = [0]
        def change(s):
            item = s["rate_limits"].get(key, {"count": 0, "at": now_ts})
            if now_ts - item.get("at", now_ts) >= window: item = {"count": 0, "at": now_ts}
            item["count"] += 1; s["rate_limits"][key] = item; result[0] = item["count"]
        self.update(change); return result[0]


class Store:
    def __new__(cls, path: str | Path | None = None):
        token = os.getenv("BLOB_READ_WRITE_TOKEN", "").strip()
        if path is None and token:
            return BlobStore(token)
        return super().__new__(cls)

    def __init__(self, path: str | Path | None = None):
        self.path = Path(path or os.getenv("EXAM_RADAR_DB", Path(__file__).parent / "data" / "exam-radar.sqlite3"))
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.lock = RLock()
        with self.connect() as db:
            db.execute("PRAGMA journal_mode=WAL")
            db.executescript("""
                CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, name TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS courses (
                    id TEXT PRIMARY KEY, owner TEXT NOT NULL REFERENCES users(id), payload TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS courses_owner ON courses(owner);
                CREATE TABLE IF NOT EXISTS shares (
                    token TEXT PRIMARY KEY, owner TEXT NOT NULL, course_id TEXT NOT NULL,
                    payload TEXT NOT NULL, created_at TEXT NOT NULL
                );
            CREATE TABLE IF NOT EXISTS comments (
                    id TEXT PRIMARY KEY, token TEXT NOT NULL REFERENCES shares(token),
                    author_id TEXT NOT NULL, author TEXT NOT NULL, body TEXT NOT NULL, created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS auth_identities (id TEXT PRIMARY KEY, provider TEXT NOT NULL, subject TEXT NOT NULL, display_name TEXT, UNIQUE(provider,subject));
                CREATE TABLE IF NOT EXISTS auth_sessions (id TEXT PRIMARY KEY, identity_id TEXT NOT NULL, user_id TEXT NOT NULL, provider TEXT NOT NULL, expires_at REAL NOT NULL, revoked INTEGER NOT NULL DEFAULT 0);
                CREATE TABLE IF NOT EXISTS oauth_states (state TEXT PRIMARY KEY, browser_id TEXT NOT NULL, redirect_uri TEXT NOT NULL, expires_at REAL NOT NULL, used INTEGER NOT NULL DEFAULT 0);
                CREATE TABLE IF NOT EXISTS login_events (id TEXT PRIMARY KEY, identity_id TEXT NOT NULL, provider TEXT NOT NULL, created_at TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS rate_limits (key TEXT PRIMARY KEY, count INTEGER NOT NULL, window_started REAL NOT NULL);
            """)

    @contextmanager
    def connect(self):
        db = sqlite3.connect(str(self.path), timeout=20)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        try:
            with db:
                yield db
        finally:
            db.close()

    def user(self, user_id: str | None):
        if not user_id:
            return None
        with self.connect() as db:
            row = db.execute("SELECT id,name FROM users WHERE id=?", (user_id,)).fetchone()
        return dict(row) if row else None

    def save_user(self, user: dict):
        with self.connect() as db:
            db.execute("INSERT INTO users(id,name) VALUES(?,?) ON CONFLICT(id) DO UPDATE SET name=excluded.name", (user["id"], user["name"]))

    def courses(self, owner: str):
        with self.connect() as db:
            rows = db.execute("SELECT payload FROM courses WHERE owner=? ORDER BY rowid", (owner,)).fetchall()
        return [json.loads(row["payload"]) for row in rows]

    def course(self, owner: str, course_id: str):
        with self.connect() as db:
            row = db.execute("SELECT payload FROM courses WHERE owner=? AND id=?", (owner, course_id)).fetchone()
        return json.loads(row["payload"]) if row else None

    def save_course(self, owner: str, course: dict):
        with self.lock, self.connect() as db:
            row = db.execute("SELECT owner FROM courses WHERE id=?", (course["id"],)).fetchone()
            if row and row["owner"] != owner:
                raise ValueError("Course belongs to another user")
            db.execute("INSERT INTO courses(id,owner,payload) VALUES(?,?,?) ON CONFLICT(id) DO UPDATE SET payload=excluded.payload", (course["id"], owner, json.dumps(course, ensure_ascii=False)))

    def create_share(self, owner: str, course_id: str, token: str, payload: dict, created_at: str):
        with self.connect() as db:
            db.execute("INSERT INTO shares VALUES(?,?,?,?,?)", (token, owner, course_id, json.dumps(payload, ensure_ascii=False), created_at))

    def share(self, token: str):
        with self.connect() as db:
            row = db.execute("SELECT payload FROM shares WHERE token=?", (token,)).fetchone()
            if not row:
                return None
            comments = db.execute("SELECT id,author,body,created_at AS createdAt FROM comments WHERE token=? ORDER BY rowid", (token,)).fetchall()
        return {**json.loads(row["payload"]), "comments": [dict(item) for item in comments]}

    def add_comment(self, token: str, user: dict, comment: dict):
        with self.connect() as db:
            db.execute("INSERT INTO comments VALUES(?,?,?,?,?,?)", (comment["id"], token, user["id"], user["name"], comment["body"], comment["createdAt"]))

    def auth_identity(self, provider: str, subject: str):
        with self.connect() as db:
            row = db.execute("SELECT id,provider,subject,display_name AS displayName FROM auth_identities WHERE provider=? AND subject=?", (provider, subject)).fetchone()
        return dict(row) if row else None
    def save_auth_identity(self, identity):
        with self.connect() as db: db.execute("INSERT INTO auth_identities(id,provider,subject,display_name) VALUES(?,?,?,?) ON CONFLICT(provider,subject) DO UPDATE SET display_name=excluded.display_name", (identity["id"],identity["provider"],identity["subject"],identity.get("displayName")))
    def save_auth_session(self, item):
        with self.connect() as db: db.execute("INSERT OR REPLACE INTO auth_sessions VALUES(?,?,?,?,?,?)", (item["id"],item["identityId"],item["userId"],item["provider"],item["expiresAt"],int(item.get("revoked",False))))
    def auth_session(self, sid):
        with self.connect() as db: row=db.execute("SELECT id,identity_id AS identityId,user_id AS userId,provider,expires_at AS expiresAt,revoked FROM auth_sessions WHERE id=?",(sid,)).fetchone()
        return dict(row) if row else None
    def revoke_auth_session(self, sid):
        with self.connect() as db: db.execute("UPDATE auth_sessions SET revoked=1 WHERE id=?",(sid,))
    def revoke_identity_sessions(self, identity_id):
        with self.connect() as db: db.execute("UPDATE auth_sessions SET revoked=1 WHERE identity_id=?",(identity_id,))
    def save_oauth_state(self, item):
        with self.connect() as db: db.execute("INSERT OR REPLACE INTO oauth_states VALUES(?,?,?,?,0)",(item["state"],item["browserId"],item["redirectUri"],item["expiresAt"]))
    def pop_oauth_state(self, state):
        with self.connect() as db:
            row=db.execute("SELECT state,browser_id AS browserId,redirect_uri AS redirectUri,expires_at AS expiresAt,used FROM oauth_states WHERE state=? AND used=0",(state,)).fetchone()
            if row: db.execute("UPDATE oauth_states SET used=1 WHERE state=?",(state,))
        return dict(row) if row else None
    def record_login(self,event):
        with self.connect() as db: db.execute("INSERT INTO login_events VALUES(?,?,?,?)",(event["id"],event["identityId"],event["provider"],event["createdAt"]))
    def login_stats(self):
        with self.connect() as db:
            total=db.execute("SELECT COUNT(*) FROM login_events").fetchone()[0]; unique=db.execute("SELECT COUNT(DISTINCT identity_id) FROM login_events").fetchone()[0]; rows=db.execute("SELECT provider,COUNT(*) n FROM login_events GROUP BY provider").fetchall()
        return {"totalLogins":total,"uniqueUsers":unique,"byProvider":{r["provider"]:r["n"] for r in rows}}
    def rate_limit(self,key,now_ts,window):
        with self.lock, self.connect() as db:
            row=db.execute("SELECT count,window_started FROM rate_limits WHERE key=?",(key,)).fetchone()
            count=0 if not row or now_ts-row["window_started"]>=window else row["count"]
            started=now_ts if not row or now_ts-row["window_started"]>=window else row["window_started"]; count+=1
            db.execute("INSERT OR REPLACE INTO rate_limits VALUES(?,?,?)",(key,count,started)); return count
