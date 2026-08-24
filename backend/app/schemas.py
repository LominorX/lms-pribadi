from pydantic import BaseModel, EmailStr
from typing import Optional

# Format data saat user mendaftar
class UserCreate(BaseModel):
    nama: str
    email: EmailStr
    password: str
    role: Optional[str] = "MURID" # Pilihan: 'GURU' atau 'MURID'

# Format data balasan dari server (tanpa menampilkan password)
class UserResponse(BaseModel):
    id: int
    nama: str
    email: EmailStr
    role: str

    class Config:
        from_attributes = True

# Format data untuk Login
class Token(BaseModel):
    access_token: str
    token_type: str
    role: str