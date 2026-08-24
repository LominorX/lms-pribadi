from fastapi import FastAPI, Depends, Form
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from .database import engine, get_db
from . import models, auth

# Membuat seluruh tabel baru secara otomatis di lms.db
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="LMS Pribadi")

CSS_STYLE = """
<style>
    * { box-sizing: border-box; font-family: 'Segoe UI', sans-serif; }
    body { background-color: #f4f7f6; margin: 0; padding: 20px; color: #333; }
    .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    h1, h2, h3 { color: #2c3e50; }
    .form-group { margin-bottom: 15px; }
    label { display: block; margin-bottom: 5px; font-weight: bold; }
    input, select, textarea { width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 5px; font-size: 14px; }
    button { background-color: #3498db; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; font-size: 14px; }
    button:hover { background-color: #2980b9; }
    .card { background: #fafafa; border-left: 4px solid #3498db; padding: 15px; margin-bottom: 15px; border-radius: 4px; }
    .badge { padding: 4px 8px; border-radius: 4px; font-size: 12px; color: white; font-weight: bold; }
    .badge-guru { background-color: #e74c3c; }
    .badge-murid { background-color: #2ecc71; }
    table { width: 100%; border-collapse: collapse; margin-top: 10px; }
    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; font-size: 13px; }
    th { background-color: #f2f2f2; }
</style>
"""

@app.get("/", response_class=HTMLResponse)
def home():
    return f"""
    <!DOCTYPE html>
    <html>
    <head><title>LMS Pribadi - Masuk</title>{CSS_STYLE}</head>
    <body>
        <div class="container" style="max-width: 450px;">
            <h2 style="text-align: center;">🎓 LMS Pribadi</h2>
            <hr><br>
            <h3>Masuk / Login</h3>
            <form action="/web-login" method="post">
                <div class="form-group"><label>Email</label><input type="email" name="email" required></div>
                <div class="form-group"><label>Password</label><input type="password" name="password" required></div>
                <button type="submit">Masuk Ke Sistem</button>
            </form>
            <br><hr><br>
            <h3>Buat Akun Baru</h3>
            <form action="/web-register" method="post">
                <div class="form-group"><label>Nama Lengkap</label><input type="text" name="nama" required></div>
                <div class="form-group"><label>Email</label><input type="email" name="email" required></div>
                <div class="form-group"><label>Password</label><input type="password" name="password" required></div>
                <div class="form-group"><label>Daftar Sebagai</label>
                    <select name="role"><option value="MURID">Murid</option><option value="GURU">Guru</option></select>
                </div>
                <button type="submit" style="background-color: #2ecc71;">Daftar Akun</button>
            </form>
        </div>
    </body>
    </html>
    """

@app.post("/web-register", response_class=HTMLResponse)
def register(nama: str = Form(...), email: str = Form(...), password: str = Form(...), role: str = Form(...), db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == email).first():
        return f"<html><head>{CSS_STYLE}</head><body><div class='container'><h3>❌ Email sudah terdaftar!</h3><a href='/'>Kembali</a></div></body></html>"
    
    new_user = models.User(nama=nama, email=email, hashed_password=auth.hash_password(password), role=role)
    db.add(new_user)
    db.commit()
    db.add(models.AuditLog(user_id=new_user.id, aksi=f"REGISTER ({role})"))
    db.commit()
    return f"<html><head>{CSS_STYLE}</head><body><div class='container'><h3>✅ Akun Berhasil Dibuat!</h3><a href='/'>Klik di sini untuk Login</a></div></body></html>"

@app.post("/web-login", response_class=HTMLResponse)
def login(email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or not auth.verify_password(password, user.hashed_password):
        return f"<html><head>{CSS_STYLE}</head><body><div class='container'><h3>❌ Email/Password Salah!</h3><a href='/'>Coba Lagi</a></div></body></html>"

    db.add(models.AuditLog(user_id=user.id, aksi="LOGIN"))
    db.commit()

    assignments = db.query(models.Assignment).all()
    badge = "badge-guru" if user.role == "GURU" else "badge-murid"

    # HTML Daftar Tugas
    tugas_html = ""
    for task in assignments:
        tugas_html += f"""
        <div class="card">
            <h4>{task.judul} (Dibuat Oleh: {task.created_by})</h4>
            <p>{task.deskripsi}</p>
        """
        if user.role == "MURID":
            tugas_html += f"""
            <form action="/submit-task" method="post">
                <input type="hidden" name="assignment_id" value="{task.id}">
                <input type="hidden" name="student_name" value="{user.nama}">
                <textarea name="jawaban" placeholder="Tulis jawaban tugasmu di sini..." required></textarea><br><br>
                <button type="submit" style="background-color: #2ecc71;">Kirim Jawaban</button>
            </form>
            """
        tugas_html += "</div>"

    # Tampilan Khusus Guru: Form Buat Tugas & Audit Log
    guru_section = ""
    if user.role == "GURU":
        logs = db.query(models.AuditLog).order_by(models.AuditLog.id.desc()).limit(5).all()
        log_rows = "".join([f"<tr><td>{l.id}</td><td>User ID: {l.user_id}</td><td>{l.aksi}</td><td>{l.timestamp.strftime('%Y-%m-%d %H:%M')}</td></tr>" for l in logs])

        guru_section = f"""
        <div class="card" style="border-left-color: #e74c3c;">
            <h3>➕ Terbitkan Tugas Baru (Fitur Guru)</h3>
            <form action="/create-task" method="post">
                <input type="hidden" name="guru_nama" value="{user.nama}">
                <div class="form-group"><input type="text" name="judul" placeholder="Judul Tugas (misal: Tugas 1 Python)" required></div>
                <div class="form-group"><textarea name="deskripsi" placeholder="Deskripsi atau Instruksi Tugas" required></textarea></div>
                <button type="submit">Terbitkan Tugas</button>
            </form>
        </div>

        <div class="card" style="border-left-color: #f39c12;">
            <h3>📋 Riwayat Audit Log Sistem (Poin 10 Silabus)</h3>
            <table>
                <tr><th>ID</th><th>User</th><th>Aksi</th><th>Waktu</th></tr>
                {log_rows}
            </table>
        </div>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head><title>Dashboard LMS</title>{CSS_STYLE}</head>
    <body>
        <div class="container">
            <h2>Halo, {user.nama}! 👋</h2>
            <p>Role: <span class="badge {badge}">{user.role}</span> | <a href="/">Logout</a></p>
            <hr><br>
            {guru_section}
            <h3>📚 Daftar Tugas</h3>
            {tugas_html if tugas_html else "<p>Belum ada tugas yang dibuat oleh Guru.</p>"}
        </div>
    </body>
    </html>
    """

@app.post("/create-task", response_class=HTMLResponse)
def create_task(judul: str = Form(...), deskripsi: str = Form(...), guru_nama: str = Form(...), db: Session = Depends(get_db)):
    new_task = models.Assignment(judul=judul, deskripsi=deskripsi, created_by=guru_nama)
    db.add(new_task)
    db.commit()
    return f"<html><head>{CSS_STYLE}</head><body><div class='container'><h3>✅ Tugas Berhasil Diterbitkan!</h3><a href='/'>Kembali ke Halaman Utama</a></div></body></html>"

@app.post("/submit-task", response_class=HTMLResponse)
def submit_task(assignment_id: int = Form(...), student_name: str = Form(...), jawaban: str = Form(...), db: Session = Depends(get_db)):
    sub = models.Submission(assignment_id=assignment_id, student_name=student_name, jawaban=jawaban)
    db.add(sub)
    db.commit()
    db.add(models.AuditLog(user_id=0, aksi=f"SUBMIT_TASK oleh {student_name}"))
    db.commit()
    return f"<html><head>{CSS_STYLE}</head><body><div class='container'><h3>✅ Jawaban Tugas Berhasil Dikirim!</h3><a href='/'>Kembali ke Halaman Utama</a></div></body></html>"