from fastapi.testclient import TestClient
from paperweave.server import app

def test_local_upload_ui_and_cross_origin_protection():
    with TestClient(app) as client:
        assert client.get('/').status_code==200
        assert client.get('/api/config').json()['ready'] in {True,False}
        assert client.get('/',headers={'host':'foreign.example'}).status_code==403
        assert client.post('/api/jobs',headers={'origin':'https://foreign.example'}).status_code==403
        assert client.get('/api/jobs/nope/files/.env').status_code==404
