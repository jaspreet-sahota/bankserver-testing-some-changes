import hmac, hashlib, os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from key_derivation import derive_keys

# Use an environment variable or secure storage to manage the master secret
# Check for None explicitly to avoid encoding errors
raw_master_secret = os.getenv('MASTER_SECRET')
if raw_master_secret is None:
    print("WARNING: MASTER_SECRET is not set. Using a default value for development.")
    MASTER_SECRET = b'default_master_secret'
else:
    MASTER_SECRET = raw_master_secret.encode()

AES_KEY, MAC_KEY = derive_keys(MASTER_SECRET)

def generate_mac(data):
    print("Data for MAC generation:", data)
    print("Key for MAC generation:", MAC_KEY)
    return hmac.new(MAC_KEY, data, hashlib.sha256).digest()

def verify_mac(data, mac_received, key):
    # Convert the key from hex string to bytes if it's not already bytes
    if isinstance(key, str):
        key_bytes = bytes.fromhex(key)
    else:
        key_bytes = key

    # Ensure the data is in bytes
    if isinstance(data, str):
        data_bytes = data.encode('utf-8')
    else:
        data_bytes = data

    # Generate the HMAC
    generated_mac = hmac.new(key_bytes, data_bytes, hashlib.sha256).digest()
    result = hmac.compare_digest(generated_mac, mac_received)
    print("Generated MAC:", generated_mac)
    print("Received MAC:", mac_received)
    print("Verification result:", result)
    return result

def encrypt(message, key):
    if isinstance(message, str):
        message = message.encode('utf-8')
    try:
        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        padded_data = padder.update(message) + padder.finalize()
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        cipher_text = encryptor.update(padded_data) + encryptor.finalize()
        return iv + cipher_text
    except Exception as e:
        raise ValueError("Encryption failed") from e

def decrypt(cipher_text, key):
    try:
        iv = cipher_text[:16]
        cipher_text = cipher_text[16:]
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_message = decryptor.update(cipher_text) + decryptor.finalize()
        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        decrypted_message = unpadder.update(padded_message) + unpadder.finalize()
        return decrypted_message
    except Exception as e:
        raise ValueError("Decryption failed") from e
