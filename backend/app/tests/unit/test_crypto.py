from app.core.crypto import encrypt, decrypt


def test_roundtrip_full():
    ssn = "123456789"

    ssn_enc, dek_enc = encrypt.encryption(ssn)
    ssn_decrypted = decrypt.decryption(ssn_enc, dek_enc)

    assert ssn == ssn_decrypted


def test_dek_roundtrip():
    dek = "123456".encode()
    dek_enc = encrypt._encrypt_kms_aes_dek(dek)
    dek_decrypted = decrypt._decrypt_kms_aes_dek(dek_enc)

    assert dek == dek_decrypted
