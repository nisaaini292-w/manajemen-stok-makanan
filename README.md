# API Manajemen Stok Makanan

**Nama:** Nisa Nafiisatul Aini | **NIM:** 21114022610034 | **Kelas:** 1B

## 1. Deskripsi Project

REST API untuk mengelola stok makanan, kategori, lokasi penyimpanan, dan riwayat transaksi stok. Dibangun dengan **Flask**, **Flask-SQLAlchemy**, dan **PostgreSQL (Supabase)**, lalu di-deploy ke **Vercel**.

Fitur utama:
- CRUD data makanan (stok otomatis dibuat saat makanan ditambahkan)
- CRUD data stok
- Pencatatan transaksi stok MASUK / KELUAR yang otomatis memperbarui jumlah stok
- Riwayat transaksi tidak bisa dihapus agar catatan stok tetap akurat

## 2. ERD / Skema Database

![ERD Manajemen Stok Makanan](erd.png)

| Tabel | Primary Key | Foreign Key |
|-------|-------------|-------------|
| kategori | id_kategori | - |
| lokasi_penyimpanan | id_lokasi | - |
| makanan | id_makanan | id_kategori, id_lokasi |
| stok | id_stok | id_makanan (unique) |
| riwayat_stok | id_riwayat | id_makanan |

Relasi:
- Satu `kategori` punya banyak `makanan` (one-to-many)
- Satu `lokasi_penyimpanan` punya banyak `makanan` (one-to-many)
- Satu `makanan` punya satu `stok` (one-to-one)
- Satu `makanan` punya banyak `riwayat_stok` (one-to-many)

## 3. URL Deployment

**https://manajemen-stok-makanan.vercel.app**

## 4. Daftar Endpoint

Semua request dan response memakai format JSON. Untuk POST dan PUT, kirim header `Content-Type: application/json`.

Format error untuk semua endpoint:

```json
{
  "status": "error",
  "message": "Penjelasan error"
}
```

### Cek API
- Method       : GET
- URL          : https://manajemen-stok-makanan.vercel.app/
- Deskripsi    : Mengecek apakah API berjalan
- Response Sukses (200):
```json
{
  "status": "success",
  "message": "API Manajemen Stok Makanan berjalan"
}
```

### Cek Koneksi Database
- Method       : GET
- URL          : https://manajemen-stok-makanan.vercel.app/db-check
- Deskripsi    : Mengecek koneksi ke database
- Response Sukses (200):
```json
{
  "status": "success",
  "message": "Database berhasil terhubung"
}
```
- Response Error (500):
```json
{
  "status": "error",
  "message": "Database gagal terhubung",
  "detail": "..."
}
```

---

## Makanan

### Lihat Semua Makanan
- Method       : GET
- URL          : https://manajemen-stok-makanan.vercel.app/makanan
- Deskripsi    : Mengambil seluruh data makanan
- Response Sukses (200):
```json
{
  "status": "success",
  "data": [
    {
      "id_makanan": 1,
      "nama_makanan": "Beras",
      "id_kategori": 1,
      "id_lokasi": 1,
      "satuan": "kg",
      "tanggal_kedaluwarsa": "2027-01-31"
    }
  ]
}
```

### Lihat Detail Makanan
- Method       : GET
- URL          : https://manajemen-stok-makanan.vercel.app/makanan/1
- Deskripsi    : Mengambil satu data makanan berdasarkan id
- Response Sukses (200):
```json
{
  "status": "success",
  "data": {
    "id_makanan": 1,
    "nama_makanan": "Beras",
    "id_kategori": 1,
    "id_lokasi": 1,
    "satuan": "kg",
    "tanggal_kedaluwarsa": "2027-01-31"
  }
}
```
- Response Error (404):
```json
{
  "status": "error",
  "message": "Data makanan tidak ditemukan"
}
```

### Tambah Makanan
- Method       : POST
- URL          : https://manajemen-stok-makanan.vercel.app/makanan
- Deskripsi    : Menambahkan makanan baru. Data stok awal (jumlah 0) dibuat otomatis
- Headers      : Content-Type: application/json
- Request Body :
```json
{
  "nama_makanan": "Beras",
  "id_kategori": 1,
  "id_lokasi": 1,
  "satuan": "kg",
  "tanggal_kedaluwarsa": "2027-01-31"
}
```
- Response Sukses (201):
```json
{
  "status": "success",
  "message": "Makanan berhasil ditambahkan",
  "data": {
    "id_makanan": 1,
    "nama_makanan": "Beras",
    "id_kategori": 1,
    "id_lokasi": 1,
    "satuan": "kg",
    "tanggal_kedaluwarsa": "2027-01-31"
  }
}
```
- Response Error (400):
```json
{
  "status": "error",
  "message": "nama_makanan dan satuan wajib diisi"
}
```
- Response Error (404):
```json
{
  "status": "error",
  "message": "Kategori tidak ditemukan"
}
```

### Ubah Makanan
- Method       : PUT
- URL          : https://manajemen-stok-makanan.vercel.app/makanan/1
- Deskripsi    : Mengubah data makanan. Kirim hanya field yang ingin diubah
- Headers      : Content-Type: application/json
- Request Body :
```json
{
  "nama_makanan": "Beras Premium",
  "satuan": "kg"
}
```
- Response Sukses (200):
```json
{
  "status": "success",
  "message": "Data makanan berhasil diperbarui",
  "data": {
    "id_makanan": 1,
    "nama_makanan": "Beras Premium",
    "id_kategori": 1,
    "id_lokasi": 1,
    "satuan": "kg",
    "tanggal_kedaluwarsa": "2027-01-31"
  }
}
```
- Response Error (404):
```json
{
  "status": "error",
  "message": "Data makanan tidak ditemukan"
}
```

### Hapus Makanan
- Method       : DELETE
- URL          : https://manajemen-stok-makanan.vercel.app/makanan/1
- Deskripsi    : Menghapus makanan beserta stoknya. Ditolak jika makanan sudah punya riwayat transaksi
- Response Sukses (200):
```json
{
  "status": "success",
  "message": "Makanan berhasil dihapus"
}
```
- Response Error (409):
```json
{
  "status": "error",
  "message": "Makanan memiliki riwayat transaksi sehingga tidak dapat dihapus"
}
```

---

## Stok

### Lihat Semua Stok
- Method       : GET
- URL          : https://manajemen-stok-makanan.vercel.app/stok
- Deskripsi    : Mengambil seluruh data stok
- Response Sukses (200):
```json
{
  "status": "success",
  "data": [
    {
      "id_stok": 1,
      "id_makanan": 1,
      "jumlah_stok": 0,
      "stok_minimum": 0,
      "tanggal_update": "2026-10-24T19:30:00"
    }
  ]
}
```

### Lihat Detail Stok
- Method       : GET
- URL          : https://manajemen-stok-makanan.vercel.app/stok/1
- Deskripsi    : Mengambil satu data stok berdasarkan id_stok
- Response Sukses (200):
```json
{
  "status": "success",
  "data": {
    "id_stok": 1,
    "id_makanan": 1,
    "jumlah_stok": 0,
    "stok_minimum": 0,
    "tanggal_update": "2026-10-24T19:30:00"
  }
}
```
- Response Error (404):
```json
{
  "status": "error",
  "message": "Data stok tidak ditemukan"
}
```

### Tambah Stok
- Method       : POST
- URL          : https://manajemen-stok-makanan.vercel.app/stok
- Deskripsi    : Menambahkan data stok untuk makanan yang belum punya stok
- Headers      : Content-Type: application/json
- Request Body :
```json
{
  "id_makanan": 1,
  "jumlah_stok": 10,
  "stok_minimum": 2
}
```
- Response Sukses (201):
```json
{
  "status": "success",
  "message": "Data stok berhasil ditambahkan",
  "data": {
    "id_stok": 1,
    "id_makanan": 1,
    "jumlah_stok": 10,
    "stok_minimum": 2,
    "tanggal_update": "2026-10-24T19:30:00"
  }
}
```
- Response Error (409):
```json
{
  "status": "error",
  "message": "Stok untuk makanan ini sudah tersedia. Gunakan PUT untuk memperbaruinya."
}
```

### Ubah Stok
- Method       : PUT
- URL          : https://manajemen-stok-makanan.vercel.app/stok/1
- Deskripsi    : Mengubah jumlah stok dan/atau stok minimum
- Headers      : Content-Type: application/json
- Request Body :
```json
{
  "jumlah_stok": 20,
  "stok_minimum": 5
}
```
- Response Sukses (200):
```json
{
  "status": "success",
  "message": "Data stok berhasil diperbarui",
  "data": {
    "id_stok": 1,
    "id_makanan": 1,
    "jumlah_stok": 20,
    "stok_minimum": 5,
    "tanggal_update": "2026-10-24T19:35:00"
  }
}
```
- Response Error (400):
```json
{
  "status": "error",
  "message": "Jumlah stok tidak boleh negatif"
}
```

### Hapus Stok
- Method       : DELETE
- URL          : https://manajemen-stok-makanan.vercel.app/stok/1
- Deskripsi    : Menghapus data stok. Ditolak jika makanan sudah punya riwayat transaksi
- Response Sukses (200):
```json
{
  "status": "success",
  "message": "Data stok berhasil dihapus"
}
```
- Response Error (409):
```json
{
  "status": "error",
  "message": "Stok memiliki riwayat transaksi sehingga tidak dapat dihapus"
}
```

---

## Riwayat Stok

### Lihat Semua Riwayat
- Method       : GET
- URL          : https://manajemen-stok-makanan.vercel.app/riwayat-stok
- Deskripsi    : Mengambil seluruh riwayat transaksi, terbaru lebih dulu
- Response Sukses (200):
```json
{
  "status": "success",
  "data": [
    {
      "id_riwayat": 1,
      "id_makanan": 1,
      "jenis_transaksi": "MASUK",
      "jumlah": 10,
      "tanggal_transaksi": "2026-10-24T19:40:00",
      "keterangan": "Belanja bulanan"
    }
  ]
}
```

### Lihat Detail Riwayat
- Method       : GET
- URL          : https://manajemen-stok-makanan.vercel.app/riwayat-stok/1
- Deskripsi    : Mengambil satu riwayat transaksi berdasarkan id_riwayat
- Response Sukses (200):
```json
{
  "status": "success",
  "data": {
    "id_riwayat": 1,
    "id_makanan": 1,
    "jenis_transaksi": "MASUK",
    "jumlah": 10,
    "tanggal_transaksi": "2026-10-24T19:40:00",
    "keterangan": "Belanja bulanan"
  }
}
```
- Response Error (404):
```json
{
  "status": "error",
  "message": "Riwayat transaksi tidak ditemukan"
}
```

### Catat Transaksi Stok
- Method       : POST
- URL          : https://manajemen-stok-makanan.vercel.app/riwayat-stok
- Deskripsi    : Mencatat transaksi MASUK atau KELUAR dan otomatis memperbarui jumlah stok
- Headers      : Content-Type: application/json
- Request Body :
```json
{
  "id_makanan": 1,
  "jenis_transaksi": "MASUK",
  "jumlah": 10,
  "keterangan": "Belanja bulanan"
}
```
- Response Sukses (201):
```json
{
  "status": "success",
  "message": "Transaksi stok berhasil dicatat",
  "data": {
    "riwayat": {
      "id_riwayat": 1,
      "id_makanan": 1,
      "jenis_transaksi": "MASUK",
      "jumlah": 10,
      "tanggal_transaksi": "2026-10-24T19:40:00",
      "keterangan": "Belanja bulanan"
    },
    "stok_sekarang": {
      "id_stok": 1,
      "id_makanan": 1,
      "jumlah_stok": 10,
      "stok_minimum": 0,
      "tanggal_update": "2026-10-24T19:40:00"
    }
  }
}
```
- Response Error (400):
```json
{
  "status": "error",
  "message": "jenis_transaksi harus MASUK atau KELUAR"
}
```
- Response Error (400, stok kurang):
```json
{
  "status": "error",
  "message": "Stok tidak mencukupi untuk transaksi keluar"
}
```

### Ubah Keterangan Riwayat
- Method       : PUT
- URL          : https://manajemen-stok-makanan.vercel.app/riwayat-stok/1
- Deskripsi    : Mengubah kolom keterangan saja (kolom lain tidak boleh diubah)
- Headers      : Content-Type: application/json
- Request Body :
```json
{
  "keterangan": "Belanja mingguan"
}
```
- Response Sukses (200):
```json
{
  "status": "success",
  "message": "Keterangan riwayat berhasil diperbarui",
  "data": {
    "id_riwayat": 1,
    "id_makanan": 1,
    "jenis_transaksi": "MASUK",
    "jumlah": 10,
    "tanggal_transaksi": "2026-10-24T19:40:00",
    "keterangan": "Belanja mingguan"
  }
}
```
- Response Error (400):
```json
{
  "status": "error",
  "message": "Hanya kolom keterangan yang dapat diperbarui"
}
```

### Hapus Riwayat
- Method       : DELETE
- URL          : https://manajemen-stok-makanan.vercel.app/riwayat-stok/1
- Deskripsi    : Riwayat transaksi sengaja tidak bisa dihapus agar catatan stok tetap akurat
- Response Error (409):
```json
{
  "status": "error",
  "message": "Riwayat transaksi tidak dapat dihapus agar catatan stok tetap akurat"
}
```

---

## 5. Cara Menjalankan Secara Lokal

1. Clone repository:
   ```
   git clone https://github.com/nisaaini292-w/manajemen-stok-makanan.git
   cd manajemen-stok-makanan
   ```
2. Buat dan aktifkan virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate
   ```
3. Install dependensi:
   ```
   pip install -r requirements.txt
   ```
4. Buat file `.env` di folder utama, lalu isi connection string database PostgreSQL:
   ```
   DATABASE_URL=postgresql://user:password@host:port/nama_database
   ```
5. Buat tabel dengan menjalankan isi `database.sql` di database PostgreSQL (misalnya lewat SQL Editor Supabase).
6. Jalankan aplikasi:
   ```
   python run.py
   ```
7. Buka `http://localhost:5000` (port bisa berbeda, lihat isi `run.py`).

> File `.env` tidak ikut di-upload ke GitHub. Saat deploy ke Vercel, `DATABASE_URL` diisi lewat **Environment Variables**.
