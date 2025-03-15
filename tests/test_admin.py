from core.config import ADMIN_SECRET
from fastapi.testclient import TestClient
from core.main import app


client = TestClient(app)
