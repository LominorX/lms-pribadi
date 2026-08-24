import hashlib

# Fungsi Enkripsi Password (Pakai SHA-256 standar Python, super stabil)
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# Fungsi Verifikasi Password saat Login
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hash_password(plain_password) == hashed_password