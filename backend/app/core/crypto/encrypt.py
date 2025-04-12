import secrets
from Crypto.Cipher import AES

import boto3
from botocore.exceptions import ClientError


def generate_256_dek():
    return secrets.token_bytes(32)


def _encrypt_aes_ssn(ssn: str, dek: bytes) -> bytes:
    cipher = AES.new(dek, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(ssn.encode())
    return cipher.nonce + tag + ciphertext  # 16 bytes + 16 bytes + cipher


def _encrypt_kms_aes_dek(dek: bytes) -> bytes:
    session = boto3.session.Session()
    kms_client = session.client(service_name="kms", region_name="ap-southeast-5")
    try:
        kms_response = kms_client.encrypt(
            KeyId="ec7f7582-86fd-464f-b62d-710b5a512aba",
            Plaintext=dek,
            EncryptionAlgorithm="SYMMETRIC_DEFAULT",
        )

        dek_enc = kms_response.get("CiphertextBlob", None)
        if not dek_enc:
            raise ValueError("Key was not encrypted.")
        return dek_enc

    except ClientError as e:
        raise e
    except Exception as e:
        raise e


def encryption(ssn: str) -> tuple[bytes, bytes]:
    dek = generate_256_dek()
    ssn_enc = _encrypt_aes_ssn(ssn, dek)
    dek_enc = _encrypt_kms_aes_dek(dek)
    return ssn_enc, dek_enc
