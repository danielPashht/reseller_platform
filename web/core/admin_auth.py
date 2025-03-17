import config

from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from jose import JWTError, jwt
from datetime import datetime, timedelta


SECRET_KEY = config.ADMIN_SECRET
ALGORITHM = "HS256"


class AdminAuth(AuthenticationBackend):
    def __init__(self, secret_key: str):
        super().__init__(secret_key)
        self.secret_key = secret_key

    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form["username"], form["password"]

        # For demo. Check in db in production.
        if username != "admin" or password != "admin":
            return False

        # For demo. In production get user_id from db.
        user_id = 1
        access_token_expires = timedelta(minutes=30)
        access_token = self.create_access_token(
            data={"sub": str(user_id)}, expires_delta=access_token_expires
        )
        request.session.update({"token": access_token})
        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")
        if not token:
            return False
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[ALGORITHM])
            user_id: str = payload.get("sub")
            # For demo. Check in db in production.
            if user_id is None:
                return False
        except JWTError:
            return False
        return True

    def create_access_token(self, data: dict, expires_delta: timedelta | None = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=30)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=ALGORITHM)
        return encoded_jwt


authentication_backend = AdminAuth(secret_key=SECRET_KEY)
