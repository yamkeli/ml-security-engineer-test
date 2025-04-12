from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.main import get_db_manager
from app.core.db.database_manager import DatabaseManager

from app.core.auth import jwt
from app.core.auth.jwt import (
    ExpiredSignatureError,
    DecodeError,
    InvalidAlgorithmError,
    InvalidSignatureError,
)

from app.core.crypto import encrypt, decrypt

from app.core.contact import form_handling
from app.core.contact.form_handling import UniqueViolation

from app.schema.form import UserContactForm
from app.schema.jwt import JWTAuthResult

contact_router = APIRouter()


@contact_router.post("/submit", status_code=201)
def submit_form(
    payload: UserContactForm,
    database_manager: DatabaseManager = Depends(get_db_manager),
    jwt_auth: JWTAuthResult = Depends(jwt.wrapped_verify_jwt),
):
    # jwt state check
    if not all(jwt_auth.payload.model_dump().values()) or jwt_auth.error != None:
        if isinstance(jwt_auth.error, ExpiredSignatureError):
            raise HTTPException(401, {"status": "Token is expired."})
        if isinstance(jwt_auth.error, DecodeError):
            raise HTTPException(400, {"status": "Error in decoding token."})
        if isinstance(jwt_auth.error, (InvalidAlgorithmError, ExpiredSignatureError)):
            raise HTTPException(401, {"status": "Token is invalid."})

    # payload content
    name = payload.name
    email = payload.email
    ssn = payload.ssn
    dob = payload.dob
    # from verified jwt
    user_id = jwt_auth.payload.sub

    # encrypt ssn, get encrypted ssn and encrypted dek
    ssn_enc, dek_enc = encrypt.encryption(ssn)
    try:
        form_handling.store_contact_info(
            name, dob, email, ssn_enc, dek_enc, user_id, database_manager
        )
    except UniqueViolation as e:
        raise HTTPException(409, {"status": "Contact info already uploaded."})

    return {"status": "Contact Info Uploaded"}


@contact_router.get("/load", status_code=200)
def load_contact_info(
    database_manager: DatabaseManager = Depends(get_db_manager),
    jwt_auth: JWTAuthResult = Depends(jwt.wrapped_verify_jwt),
):
    # jwt state check
    if not all(jwt_auth.payload.model_dump().values()) or jwt_auth.error != None:
        if isinstance(jwt_auth.error, ExpiredSignatureError):
            raise HTTPException(401, {"status": "Token is expired."})
        if isinstance(jwt_auth.error, DecodeError):
            raise HTTPException(400, {"status": "Error in decoding token."})
        if isinstance(jwt_auth.error, (InvalidAlgorithmError, ExpiredSignatureError)):
            raise HTTPException(401, {"status": "Token is invalid."})
    # from verified jwt
    user_id = jwt_auth.payload.sub

    # retrieve info
    name, email, dob, ssn_enc, dek_enc, user_id = form_handling.load_contact_info(
        user_id, database_manager
    )

    ssn = decrypt.decryption(bytes(ssn_enc), bytes(dek_enc))

    return {"name": name, "email": email, "dob": dob, "ssn": ssn}
