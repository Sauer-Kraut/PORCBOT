import os
import pickle
import json
from cryptography.fernet import Fernet

class SecurityModule:
    def __init__(self):
        secret_key = self.get_key()
        self.fernet = Fernet(secret_key)

    def encrypt(self, data):
        # TODO: Why dont we just encode in here?
        data_serialized = json.dumps(data)
        data_bytes = pickle.dumps(data_serialized)
        data_decrypted = self.fernet.encrypt(data_bytes)
        return data_decrypted.decode("utf-8")

    def decrypt(self, encrypted_data):
        data_encoded = encrypted_data.encode("utf-8")
        data_decrypted = self.fernet.decrypt(data_encoded)
        data_serialized = pickle.loads(data_decrypted)
        return json.loads(data_serialized)

    @staticmethod
    def get_key():
        filepath = os.path.join("secrets", "secret_key.key")
        if os.path.exists(filepath):
            return open(filepath, 'rb').read()
        else:
            raise f"Unable to find secret_key.key in {filepath}"

if __name__ == "__main__":
    securityModule = SecurityModule()
    data = "very sensitive data"
    encrypted_data = securityModule.encrypt(data)
    decrypted_data = securityModule.decrypt(encrypted_data)
    print(f"original: {data}\nencrypted (first 10 characters): {encrypted_data[:10]}\ndecrypted: {decrypted_data}")

    data_1 = securityModule.encrypt("Hello, Im Data")
    data_2 = securityModule.encrypt("Hello, Im Data")
    print(f"Data 1: {data_1}\nData 2: {data_2}")

