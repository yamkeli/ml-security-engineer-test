from pydantic import BaseModel


class UserJWTPayload(BaseModel):
    sub: str
    name: str
    iat: int
    exp: int


class JWTAuthResult:
    def __init__(self, payload: dict, error: Exception | None):
        self.payload = UserJWTPayload(**payload)
        self.error = error
