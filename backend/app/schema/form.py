from datetime import date, timedelta
from pydantic import AfterValidator, BaseModel, BeforeValidator, EmailStr
from typing import Annotated
import re


def name_only_alphabets(v: str) -> str:
    if not v.replace(" ", "").isalpha():
        raise ValueError("Name must contain only alphabets and spaces")
    return v


def validate_dob_iso(v: str) -> str:
    # dob must be a string in ISO format before parsing to `date`
    if isinstance(v, str):
        try:
            # This will raise ValueError if the format is incorrect
            return date.fromisoformat(v)
        except ValueError:
            raise ValueError("Date of birth must be in ISO format (YYYY-MM-DD)")
    return v


def validate_dob_adult(v: date) -> date:
    if not (date.today() - v > timedelta(days=18 * 365.25)):
        raise ValueError("Date of birth must be in ISO format (YYYY-MM-DD)")
    return v


def validate_ssn_format(v: str) -> str:
    # Valid SSN format: "123-45-6789"
    ssn_pattern = r"^\d{3}-\d{2}-\d{4}$"
    if not re.match(ssn_pattern, v):
        raise ValueError("SSN must be in the format XXX-XX-XXXX")
    return v


class UserContactForm(BaseModel):
    name: Annotated[str, AfterValidator(name_only_alphabets)]
    dob: Annotated[
        date, AfterValidator(validate_dob_adult), BeforeValidator(validate_dob_iso)
    ]
    email: EmailStr
    ssn: Annotated[str, AfterValidator(validate_ssn_format)]
