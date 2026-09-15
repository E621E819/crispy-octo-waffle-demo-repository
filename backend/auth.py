"""Authentication helpers. Provider URLs are configuration only; no endpoint is guessed."""
from __future__ import annotations
import hashlib, hmac, os, secrets, time
from urllib.parse import urlencode

AUTH_COOKIE = "exam_radar_auth"
BROWSER_COOKIE = "exam_radar_browser"
SESSION_TTL = 60 * 60 * 24 * 30
STATE_TTL = 600

def reviewer_enabled() -> bool:
    return bool(os.getenv("EXAM_RADAR_REVIEWER_USERNAME", "").strip() and os.getenv("EXAM_RADAR_REVIEWER_PASSWORD", ""))

def zhihu_config() -> dict:
    values = {k: os.getenv(k, "").strip() for k in ("ZHIHU_AUTHORIZATION_URL", "ZHIHU_TOKEN_URL", "ZHIHU_USERINFO_URL", "ZHIHU_SCOPE", "ZHIHU_USER_ID_FIELD")}
    verified = os.getenv("ZHIHU_OAUTH_VERIFIED", "false").strip().lower() == "true"
    urls_ok = all(values[k].startswith("https://") for k in ("ZHIHU_AUTHORIZATION_URL", "ZHIHU_TOKEN_URL", "ZHIHU_USERINFO_URL"))
    credentials_ok = bool(os.getenv("ZHIHU_CLIENT_ID", "").strip() and os.getenv("ZHIHU_CLIENT_SECRET", "").strip() and os.getenv("ZHIHU_REDIRECT_URI", "").strip())
    enabled = verified and urls_ok and credentials_ok
    reason = "" if enabled else ("知乎 OAuth 未启用：等待官方端点确认。" if not verified else ("知乎 OAuth 配置必须包含全部 HTTPS 端点及客户端凭据。" if not urls_ok or not credentials_ok else "知乎 OAuth 当前不可用。"))
    return {"reviewerEnabled": reviewer_enabled(), "zhihuEnabled": enabled, "zhihuReason": reason}

def constant_time_equal(a: str, b: str) -> bool:
    return hmac.compare_digest((a or "").encode(), (b or "").encode())

def random_id(prefix: str) -> str:
    return f"{prefix}_{secrets.token_urlsafe(24)}"

def safe_redirect(request, configured: str = "") -> str:
    base = str(request.base_url).rstrip("/")
    candidate = configured.strip() or f"{base}/api/auth/zhihu/callback"
    from urllib.parse import urlsplit
    parsed, origin = urlsplit(candidate), urlsplit(base)
    if parsed.scheme != origin.scheme or parsed.netloc != origin.netloc or parsed.path != "/api/auth/zhihu/callback":
        raise ValueError("Invalid OAuth redirect URI")
    return candidate

def authorization_url(request, state: str, redirect_uri: str) -> str:
    cfg = zhihu_config()
    endpoint = os.getenv("ZHIHU_AUTHORIZATION_URL", "").strip()
    if not cfg["zhihuEnabled"] or not endpoint:
        raise ValueError("知乎 OAuth 当前不可用")
    params = {"response_type": "code", "client_id": os.getenv("ZHIHU_CLIENT_ID", "").strip(), "redirect_uri": redirect_uri, "state": state}
    if os.getenv("ZHIHU_SCOPE", "").strip(): params["scope"] = os.getenv("ZHIHU_SCOPE").strip()
    return endpoint + ("&" if "?" in endpoint else "?") + urlencode(params)
