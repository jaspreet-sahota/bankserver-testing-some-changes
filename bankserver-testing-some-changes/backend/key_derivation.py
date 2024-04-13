import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.backends import default_backend

def derive_keys(master_secret, salt=None):
    if salt is None:
        salt = os.urandom(16)
    info_encryption = b'default_master_secret'
    info_mac = b'default_master_secret'
    hkdf_encryption = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        info=info_encryption,
        backend=default_backend()
    )
    hkdf_mac = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        info=info_mac,
        backend=default_backend()
    )
    encryption_key = hkdf_encryption.derive(master_secret)
    mac_key = hkdf_mac.derive(master_secret)
    return encryption_key, mac_key