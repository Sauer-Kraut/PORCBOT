import os
from cryptography.fernet import Fernet

class SecurityModule:
    def __init__(self):
        secret_key = self.get_key()
        self.fernet = Fernet(secret_key)

    def encrypt(self, data):
        return self.fernet.encrypt(data)

    def decrypt(self, encrypted_data):
        return self.fernet.decrypt(encrypted_data)

    @staticmethod
    def get_key():
        filepath = os.path.join("secrets", "secret_key.key")
        if os.path.exists(filepath):
            return open(filepath, 'rb').read()
        else:
            raise f"Unable to find secret_key.key in {filepath}"

if __name__ == "__main__":
    securityModule = SecurityModule()
    data = "very sensitive data".encode()
    encrypted_data = securityModule.encrypt(data)
    decrypted_data = securityModule.decrypt(encrypted_data)
    print(f"original: {data}\nencrypted (first 10 characters): {encrypted_data[:10]}\ndecrypted: {decrypted_data}")

