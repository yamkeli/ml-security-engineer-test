import re
from typing_extensions import Self
from pydantic import BaseModel, field_validator, AfterValidator, model_validator
from typing import Annotated


def validate_password(password: str) -> str:
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long.")
    if not re.search(r"[A-Z]", password):
        raise ValueError("Password must contain an uppercase letter.")
    if not re.search(r"[a-z]", password):
        raise ValueError("Password must contain a lowercase letter.")
    if not re.search(r"[0-9]", password):
        raise ValueError("Password must contain a digit.")
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>\/?]', password):
        raise ValueError("Password must contain a special character.")
    return password


def validate_username(username: str) -> str:
    if not username:
        raise ValueError("Username is required.")
    if len(username) < 3 and len(username) > 64:
        raise ValueError("Username must be between 3 and 64 characters long.")
    if not username.isalnum():
        raise ValueError("Username must be alphanumeric.")
    if not bool(re.fullmatch(r"^[a-zA-Z][a-zA-Z0-9_-]*[a-zA-Z0-9]$", username)):
        raise ValueError(
            "Username should only contain alphanumeric characters and underscore(_) or dash(-). It must start and end with alphabets."
        )
    return username


class _UserBase(BaseModel):
    username: Annotated[str, AfterValidator(validate_username)]


class UserSignup(_UserBase):
    password: Annotated[str, AfterValidator(validate_password)]
    confirm_password: str

    @model_validator(mode="after")
    def check_passwords_match(self) -> Self:
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self


class UserLogin(_UserBase):
    password: Annotated[str, AfterValidator(validate_password)]
