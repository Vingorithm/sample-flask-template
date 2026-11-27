# Flask App Template

Template project Flask yang bisa dipakai ulang: **Python 3.12.7 · Flask 3 · Tailwind CSS v4 · SQLAlchemy 2 + Alembic · Waitress di belakang Apache (HTTPS)**.
Development memakai **SQLite**, production memakai **MySQL 5.6**.

---

## Struktur folder

```
.
├── app/                        # Paket aplikasi
│   ├── __init__.py             # create_app() — application factory
│   ├── config.py               # Development / Testing / Production config (dibaca dari .env)
│   ├── extensions.py           # db, migrate, csrf (+ naming convention constraint)
│   ├── logging_setup.py        # Log ke console + file rotasi (logs/app.log)
│   ├── security.py             # Security headers dasar
│   ├── errors.py               # Error handler: HTML untuk browser, JSON untuk /api
│   ├── template_helpers.py     # app_name, current_year, asset_url() di semua template
│   ├── cli.py                  # Perintah `flask seed`, `flask check-db`
│   ├── models/                 # Model SQLAlchemy (base.py = mixin & aturan MySQL 5.6)
│   ├── blueprints/
│   │   ├── main/               # Halaman web
│   │   └── api/                # Endpoint JSON (/api/health)
│   ├── templates/
│   │   ├── base.html           # Layout utama
│   │   ├── partials/           # navbar, flash, footer
│   │   ├── main/               # Template per blueprint
│   │   └── errors/error.html   # Satu template untuk semua error
│   └── static/
│       ├── src/input.css       # Sumber Tailwind (token desain + komponen)
│       ├── css/app.css         # Hasil build (tidak di-commit)
│       ├── js/app.js           # csrfFetch() helper
│       └── img/
├── migrations/                 # Alembic (Flask-Migrate)
├── tests/                      # pytest
├── deploy/
│   ├── apache/flaskapp.conf    # VirtualHost HTTPS + reverse proxy
│   ├── mysql/init.sql          # Buat database & user MySQL 5.6
│   ├── windows/install-service.ps1  # Waitress sebagai Windows service (NSSM)
│   └── linux/flaskapp.service  # Waitress sebagai systemd service
├── scripts/
│   ├── setup.ps1               # Setup otomatis (Windows)
│   └── setup.sh                # Setup otomatis (Linux)
├── instance/                   # File lokal per mesin: dev.db, config.py override (tidak di-commit)
├── logs/                       # Log aplikasi (tidak di-commit)
├── requirements/
│   ├── base.txt                # Dependensi inti
│   ├── prod.txt                # + waitress, PyMySQL
│   └── dev.txt                 # + pytest, ruff
├── wsgi.py                     # Entry point WSGI (flask CLI, tests)
├── serve.py                    # Entry point produksi (Waitress)
├── .env.example                # Semua variabel konfigurasi, terdokumentasi
├── .flaskenv                   # FLASK_APP (publik)
├── .python-version             # 3.12.7
├── package.json                # Tailwind CLI
└── pyproject.toml              # Konfigurasi ruff, pytest, coverage
```

---

## Prasyarat

- **Python 3.12.x** — Windows: installer dari python.org (`py -0p` untuk cek versi terpasang)
- **Node.js LTS** — hanya untuk build Tailwind
- Production: **Apache 2.4** (mod_ssl, mod_proxy, mod_proxy_http, mod_headers, mod_rewrite) dan **MySQL 5.6**

---

## Mulai cepat (development)

**Windows (PowerShell):**

```powershell
.\scripts\setup.ps1
.\.venv\Scripts\Activate.ps1
flask run                 # http://127.0.0.1:5000 — Tailwind watcher ikut jalan otomatis
```

**Linux/macOS:**

```bash
./scripts/setup.sh
source .venv/bin/activate
flask run
```

Di mode development, `flask run` otomatis menjalankan Tailwind watcher ([app/dev_assets.py](app/dev_assets.py)), sehingga CSS ter-rebuild setiap kali template diubah dan watcher ikut berhenti saat server dihentikan. Kalau ingin menjalankan Tailwind sendiri, set `TAILWIND_WATCH=false` di `.env` lalu pakai `npm run dev` di terminal terpisah.

Script setup akan: membuat `.venv` dengan Python 3.12, install dependensi, membuat `.env` dengan `SECRET_KEY` acak, build CSS, lalu menjalankan `flask db upgrade`.

<details>
<summary>Setup manual (tanpa script)</summary>

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements\dev.txt
copy .env.example .env          # lalu isi SECRET_KEY
npm install
npm run build
flask db upgrade
```
</details>

---

## Perintah sehari-hari

| Tugas | Perintah |
|---|---|
| Jalankan server dev (+ Tailwind watch) | `flask run` |
| Build CSS produksi | `npm run build` |
| Buat migrasi setelah ubah model | `flask db migrate -m "keterangan"` |
| Terapkan migrasi | `flask db upgrade` |
| Batalkan migrasi terakhir | `flask db downgrade` |
| Isi data contoh | `flask seed` |
| Cek koneksi database | `flask check-db` |
| Daftar route | `flask routes` |
| Test + coverage | `pytest --cov` |
| Lint / format | `ruff check .` / `ruff format .` |

> Selalu periksa file migrasi hasil `flask db migrate` di `migrations/versions/` sebelum di-commit — autogenerate tidak selalu sempurna (misalnya rename kolom terdeteksi sebagai drop + add).

---

## Konfigurasi

Semua pengaturan lewat `.env` (lihat [.env.example](.env.example) untuk daftar lengkap dan penjelasannya). Kelas config ada di [app/config.py](app/config.py), dipilih dengan `APP_ENV`:

| `APP_ENV` | Database default | Catatan |
|---|---|---|
| `development` | SQLite `instance/dev.db` | DEBUG aktif |
| `testing` | SQLite in-memory | CSRF nonaktif, dipakai pytest |
| `production` | MySQL dari `DB_*` atau `DATABASE_URL` | Cookie secure, log ke file, **gagal start** jika `SECRET_KEY` (< 32 karakter) atau database belum diisi |

Override khusus satu mesin (tanpa mengubah `.env`) bisa ditaruh di `instance/config.py`.

---

## Catatan MySQL 5.6

- Buat database dengan `utf8mb4` — gunakan [deploy/mysql/init.sql](deploy/mysql/init.sql).
- **Kolom VARCHAR yang di-index/unique maksimal 191 karakter** (batas index InnoDB 767 byte di 5.6). Pakai konstanta `INDEXED_STRING_MAX` dari [app/models/base.py](app/models/base.py).
- **Jangan pakai tipe kolom `JSON`** — belum ada di 5.6. Simpan sebagai `Text` jika perlu.
- `DATETIME` disimpan sebagai UTC tanpa timezone (`utcnow()` di `models/base.py`).
- `pool_recycle` (default 280 detik) harus lebih kecil dari `wait_timeout` MySQL, agar tidak muncul error *"MySQL server has gone away"*.
- `DB_POOL_SIZE` sebaiknya ≥ `WAITRESS_THREADS`.
- Migrasi dibuat dengan *batch mode* sehingga file migrasi yang sama berjalan di SQLite (dev) dan MySQL (prod). Uji migrasi baru ke MySQL staging sebelum production.

---

## Deploy ke production

Arsitektur:

```
Browser ──HTTPS──▶ Apache :443 ──HTTP──▶ Waitress 127.0.0.1:8000 ──▶ Flask ──▶ MySQL
                     │
                     └── /static/ disajikan langsung oleh Apache
```

1. **Salin kode** ke server (misalnya `C:\sites\flaskapp` atau `/srv/flaskapp`).
2. **Siapkan MySQL**: edit lalu jalankan `deploy/mysql/init.sql`.
3. **Setup aplikasi**:
   - Windows: `.\scripts\setup.ps1 -Prod`
   - Linux: `./scripts/setup.sh --prod`

   Isi `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` di `.env`, lalu jalankan script sekali lagi (untuk migrasi). Cek dengan `flask check-db`.
4. **Jalankan Waitress sebagai service**:
   - Windows: `.\deploy\windows\install-service.ps1` (butuh [NSSM](https://nssm.cc))
   - Linux: salin `deploy/linux/flaskapp.service` ke `/etc/systemd/system/`, sesuaikan path, `systemctl enable --now flaskapp`
5. **Apache**: edit baris `Define` di [deploy/apache/flaskapp.conf](deploy/apache/flaskapp.conf) (domain, path, sertifikat), include dari `httpd.conf`, lalu `httpd -t` dan restart Apache.
6. **Cek**: `https://domain-anda/api/health` harus mengembalikan `{"status": "ok", "database": "ok"}`.

**Update versi baru:**

```powershell
git pull
.\.venv\Scripts\pip install -r requirements\prod.txt
npm ci; npm run build
.\.venv\Scripts\flask db upgrade
Restart-Service flaskapp        # Linux: sudo systemctl restart flaskapp
```

**Kenapa begini:**
- Waitress hanya listen di `127.0.0.1` dan hanya mempercayai header `X-Forwarded-*` dari Apache (`WAITRESS_TRUSTED_PROXY`), sehingga `request.scheme` = `https` dan `request.remote_addr` = IP klien asli.
- Apache menangani TLS, HSTS, redirect HTTP→HTTPS, dan file statis (dengan cache panjang; `asset_url()` menambahkan `?v=<mtime>` agar file baru langsung terambil setelah deploy).
- Jika beberapa aplikasi berjalan di satu Apache, ganti nama variabel `Define` (misalnya `APP1_ROOT`) karena `Define` bersifat global, dan beri tiap app `WAITRESS_PORT` berbeda.

---

## Memakai template ini untuk project baru

1. Salin folder ini (tanpa `.venv`, `node_modules`, `.env`, `instance/*`, `logs/*`).
2. Ubah `name` di `pyproject.toml` dan `package.json`, serta `APP_NAME` di `.env`.
3. Ganti model contoh `User` sesuai kebutuhan. Jika skemanya berbeda total, hapus isi `migrations/versions/` lalu buat migrasi awal baru: `flask db migrate -m "initial schema"`.
4. Sesuaikan warna/font di blok `@theme` pada `app/static/src/input.css`.
5. Jalankan `scripts/setup.ps1` (atau `setup.sh`).

### Menambah fitur (blueprint baru)

```
app/blueprints/blog/
├── __init__.py     # bp = Blueprint("blog", __name__); from . import routes
└── routes.py       # @bp.get("/") ...
app/templates/blog/index.html
```

Daftarkan di `register_blueprints()` dalam [app/__init__.py](app/__init__.py):

```python
from .blueprints.blog import bp as blog_bp
app.register_blueprint(blog_bp, url_prefix="/blog")
```

Model baru: buat file di `app/models/`, import di `app/models/__init__.py`, lalu `flask db migrate`.

### Form & CSRF

CSRF aktif global (Flask-WTF). Di form HTML tambahkan:

```html
<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
```

Untuk request AJAX gunakan `csrfFetch(url, { method: "POST", ... })` dari `static/js/app.js`, yang otomatis mengirim header `X-CSRFToken`.

---

## Mengunci versi dependensi

`requirements/*.txt` memakai rentang versi (misalnya `Flask>=3.1,<4`). Untuk build production yang 100% reproducible, setelah setup di server staging jalankan:

```bash
pip freeze > requirements/lock.txt
```

lalu install production dengan `pip install -r requirements/lock.txt`.
