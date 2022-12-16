from cryptography.fernet import Fernet

def decrypt(key, encrypted_password):
    """
    key: String Format
    encrypted_password: Byte Format
    """
    f = Fernet(key)
    decrypted = f.decrypt(encrypted_password)

    return decrypted.decode()
    

    
