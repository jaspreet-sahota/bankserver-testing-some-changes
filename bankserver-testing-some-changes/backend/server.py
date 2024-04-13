import base64
import json
from flask import Flask, request, jsonify
from datetime import datetime
from flask_cors import CORS
import encryption
from key_derivation import derive_keys
import hashlib
import os
import hmac

app = Flask(__name__)
CORS(app)

# Use an environment variable or secure storage for the master secret
# Provide a default value to prevent errors if the environment variable is not set
MASTER_SECRET = os.getenv('MASTER_SECRET', 'default_master_secret').encode()
AES_KEY, MAC_KEY = derive_keys(MASTER_SECRET)

# Account data should ideally be stored in a secure database
accounts = {
    'Alice': {'password': hashlib.sha256('password123'.encode()).hexdigest(), 'balance': 1000},
    'Bob': {'password': hashlib.sha256('securepwd'.encode()).hexdigest(), 'balance': 500},
    'Eve': {'password': hashlib.sha256('password'.encode()).hexdigest(), 'balance': 2000}
}

user_salts = {
    'Alice': 'somerandomsalt1',
    'Bob': 'somerandomsalt2',
    'Eve': 'somerandomsalt3'
}

@app.route('/get_salt', methods=['GET'])
def get_salt():
    username = request.args.get('username')
    if username in user_salts:
        salt = user_salts[username]
        return jsonify({'salt': salt})
    else:
        return jsonify({'message': 'User not found'}), 404
    
AUDIT_LOG_FILE = "audit_log.txt"

def log_transaction(username, action, amount):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(AUDIT_LOG_FILE, "a") as file:
        file.write(f"Username: {username}, Action: {action}, Amount: {amount}, Time: {now}\n")

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    received_hashed_password = data.get('password')
    mac_received = base64.b64decode(data.get('mac'))

    if username in accounts:
        stored_hashed_password = accounts[username]['password']

        if received_hashed_password == stored_hashed_password:
            # Assuming the plaintext password is passed securely somehow or simulated here for HMAC
            plaintext_password = "password123"  # This should ideally be secure or passed differently
            if encryption.verify_mac(plaintext_password, mac_received, received_hashed_password):
                return jsonify({'message': 'Login successful', 'authenticated': True})
            else:
                return jsonify({'message': 'MAC verification failed', 'authenticated': False}), 403
        else:
            return jsonify({'message': 'Password mismatch', 'authenticated': False}), 403

    return jsonify({'message': 'Username not found', 'authenticated': False}), 404

@app.route('/transaction/deposit', methods=['POST'])
def deposit():
    data = request.get_json()
    username = data.get('username')
    encrypted_data = base64.b64decode(data.get('encryptedData'))
    mac_received = base64.b64decode(data.get('hmac'))

    if username not in accounts:
        return jsonify({'message': 'User not found'}), 404

    user_specific_key = MAC_KEY

    generated_mac = hmac.new(user_specific_key, encrypted_data, hashlib.sha256).digest()

    if not hmac.compare_digest(mac_received, generated_mac):
        print(f"Debug Info - Received MAC: {mac_received}")
        print(f"Debug Info - Generated MAC: {generated_mac}")
        print(f"Debug Info - Used MAC Key: {user_specific_key.hex()}")
        print(f"Debug Info - Used Encrypted Data: {encrypted_data.hex()}")
        return jsonify({'message': 'MAC verification failed'}), 403

    decrypted_data = encryption.decrypt(encrypted_data, AES_KEY)
    transaction_data = json.loads(decrypted_data.decode())
    amount = transaction_data.get('amount')

    accounts[username]['balance'] += amount
    log_transaction(username, 'deposit', amount)
    return jsonify({'message': 'Deposit successful', 'new_balance': accounts[username]['balance']})


@app.route('/transaction/withdraw', methods=['POST'])
def withdraw():
    data = request.get_json()
    encrypted_data = base64.b64decode(data.get('encryptedData'))
    mac_received = base64.b64decode(data.get('hmac'))

    if not encryption.verify_mac(encrypted_data, mac_received, MAC_KEY):
        return jsonify({'message': 'MAC verification failed'}), 403

    decrypted_data = encryption.decrypt(encrypted_data, AES_KEY)
    transaction_data = json.loads(decrypted_data.decode())
    username = transaction_data['username']
    amount = transaction_data['amount']

    if username in accounts and accounts[username]['balance'] >= amount:
        accounts[username]['balance'] -= amount
        log_transaction(username, 'withdraw', amount)
        return jsonify({'message': 'Withdrawal successful', 'new_balance': accounts[username]['balance']})
    else:
        return jsonify({'message': 'Insufficient funds'}), 403

@app.route('/balance/<username>', methods=['GET'])
def check_balance(username):
    if username in accounts:
        balance = accounts[username]['balance']
        return jsonify({'balance': balance})
    else:
        return jsonify({'message': 'User not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)