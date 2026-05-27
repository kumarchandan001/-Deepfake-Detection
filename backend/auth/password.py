import bcrypt

class PasswordHasher:
    """
    Handles secure one-way encryption hashing and matching validations
    for enterprise user management using standard native bcrypt cryptography.
    """
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Encrypts a raw string password into a secure bcrypt hash string.
        """
        pwd_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(pwd_bytes, salt)
        return hashed.decode('utf-8')

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Validates a raw password against its stored bcrypt hash signature.
        """
        try:
            plain_bytes = plain_password.encode('utf-8')
            hashed_bytes = hashed_password.encode('utf-8')
            return bcrypt.checkpw(plain_bytes, hashed_bytes)
        except Exception:
            return False
