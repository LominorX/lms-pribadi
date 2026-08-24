from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from datetime import datetime
from .database import Base

# 1. Tabel User (Guru & Murid)
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nama = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="MURID")  # Pilihan: 'GURU' atau 'MURID'
    created_at = Column(DateTime, default=datetime.utcnow)

# 2. Tabel Audit Log (Poin 10 Silabus)
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    aksi = Column(String, nullable=False) # Contoh: 'REGISTER', 'LOGIN', 'SUBMIT_TASK'
    timestamp = Column(DateTime, default=datetime.utcnow)

# 3. Tabel Tugas dari Guru (BARU DITAMBAHKAN)
class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    judul = Column(String, nullable=False)
    deskripsi = Column(Text, nullable=False)
    created_by = Column(String, nullable=False) # Nama Guru yang membuat
    created_at = Column(DateTime, default=datetime.utcnow)

# 4. Tabel Pengumpulan Jawaban Murid (BARU DITAMBAHKAN)
class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id"), nullable=False)
    student_name = Column(String, nullable=False) # Nama Murid yang menjawab
    jawaban = Column(Text, nullable=False)
    submitted_at = Column(DateTime, default=datetime.utcnow)