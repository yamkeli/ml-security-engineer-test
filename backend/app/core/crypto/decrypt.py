import secrets
from Crypto.Cipher import AES

import boto3
from botocore.exceptions import ClientError

from app.api.v1.config import kms_key

SSN_KEK_KEY = kms_key["ssn_kek"]


def _decrypt_aes_ssn(blob: bytes, dek: bytes) -> bytes:
    nonce = blob[:16]  # first 16 bytes
    tag = blob[16:32]  # next 16 bytes
    ciphertext = blob[32:]
    cipher = AES.new(dek, AES.MODE_GCM, nonce=nonce)
    return cipher.decrypt_and_verify(ciphertext, tag)


def _decrypt_kms_aes_dek(dek_enc: bytes) -> bytes:
    session = boto3.session.Session()
    kms_client = session.client(service_name="kms", region_name="ap-southeast-5")
    try:
        kms_response = kms_client.decrypt(
            KeyId=SSN_KEK_KEY,
            CiphertextBlob=dek_enc,
            EncryptionAlgorithm="SYMMETRIC_DEFAULT",
        )

        dek = kms_response.get("Plaintext", None)
        if not dek:
            raise ValueError("Key was not decrypted.")
        return dek

    except ClientError as e:
        raise e
    except Exception as e:
        raise e


def decryption(ssn_enc: bytes, dek_enc: bytes) -> str:
    dek = _decrypt_kms_aes_dek(dek_enc)
    ssn = _decrypt_aes_ssn(ssn_enc, dek)
    return ssn.decode()
