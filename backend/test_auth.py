import time
from fastapi.testclient import TestClient
from backend.app import create_app

def setup(monkeypatch):
    monkeypatch.setenv("EXAM_RADAR_REVIEWER_USERNAME", "judge")
    monkeypatch.setenv("EXAM_RADAR_REVIEWER_PASSWORD", "secret")
    monkeypatch.setenv("EXAM_RADAR_ADMIN_TOKEN", "admin-token")

def test_reviewer_isolated_and_idempotent(tmp_path, monkeypatch):
    setup(monkeypatch); app=create_app(tmp_path/"auth.sqlite3"); one=TestClient(app); two=TestClient(app)
    assert one.post('/api/auth/reviewer',json={'username':'judge','password':'secret'}).status_code==200
    assert one.get('/api/auth/me').json()['provider']=='reviewer'
    assert one.post('/api/auth/reviewer',json={'username':'judge','password':'secret'}).status_code==200
    assert two.post('/api/auth/reviewer',json={'username':'judge','password':'bad'}).status_code==401
    assert two.post('/api/auth/reviewer',json={'username':'judge','password':'secret'}).status_code==200
    assert one.get('/api/bootstrap').json()['user']['id'] != two.get('/api/bootstrap').json()['user']['id']
    assert one.get('/api/admin/login-stats',headers={'Authorization':'Bearer admin-token'}).json()['uniqueUsers']==1

def test_logout_and_admin_guard(tmp_path, monkeypatch):
    setup(monkeypatch); c=TestClient(create_app(tmp_path/"auth.sqlite3"))
    c.post('/api/auth/reviewer',json={'username':'judge','password':'secret'})
    assert c.post('/api/auth/logout').json()['ok']
    assert c.get('/api/auth/me').json()['authenticated'] is False
    assert c.get('/api/admin/login-stats').status_code==403

def test_zhihu_disabled_without_verified_config(tmp_path, monkeypatch):
    monkeypatch.delenv('ZHIHU_OAUTH_VERIFIED', raising=False)
    c=TestClient(create_app(tmp_path/"auth.sqlite3"))
    cfg=c.get('/api/auth/config').json(); assert cfg['zhihuEnabled'] is False
    assert c.get('/api/auth/zhihu/start').status_code==503
