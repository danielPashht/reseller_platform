from web.core.config import ADMIN_SECRET
from fastapi.testclient import TestClient
from web.core.main import app


client = TestClient(app)
