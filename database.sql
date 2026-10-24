-- Nama  : Nisa Nafiisatul Aini
-- NIM   : 21114022610034
-- Kelas : 1B

-- Tabel 1: Kategori makanan

CREATE TABLE kategori (
    id_kategori SERIAL PRIMARY KEY,
    nama_kategori VARCHAR(100) NOT NULL,
    deskripsi TEXT
);


-- Tabel 2: Lokasi Penyimpanan

CREATE TABLE lokasi_penyimpanan (
    id_lokasi SERIAL PRIMARY KEY,
    nama_lokasi VARCHAR(100) NOT NULL,
    keterangan TEXT
);


-- Tabel 3: Data makanan

CREATE TABLE makanan (
    id_makanan SERIAL PRIMARY KEY,
    nama_makanan VARCHAR(150) NOT NULL,
    id_kategori INT NOT NULL,
    id_lokasi INT NOT NULL,
    satuan VARCHAR(30) NOT NULL,
    tanggal_kedaluwarsa DATE,

    CONSTRAINT fk_makanan_kategori
        FOREIGN KEY (id_kategori)
        REFERENCES kategori(id_kategori)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_makanan_lokasi
        FOREIGN KEY (id_lokasi)
        REFERENCES lokasi_penyimpanan(id_lokasi)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);


-- Tabel 4: Stok makanan

CREATE TABLE stok (
    id_stok SERIAL PRIMARY KEY,
    id_makanan INT NOT NULL UNIQUE,
    jumlah_stok INT NOT NULL DEFAULT 0,
    stok_minimum INT NOT NULL DEFAULT 0,
    tanggal_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_stok_makanan
        FOREIGN KEY (id_makanan)
        REFERENCES makanan(id_makanan)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT cek_jumlah_stok
        CHECK (jumlah_stok >= 0),

    CONSTRAINT cek_stok_minimum
        CHECK (stok_minimum >= 0)
);


-- Tabel 5: Riwayat stok

CREATE TABLE riwayat_stok (
    id_riwayat SERIAL PRIMARY KEY,
    id_makanan INT NOT NULL,
    jenis_transaksi VARCHAR(10) NOT NULL,
    jumlah INT NOT NULL,
    tanggal_transaksi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    keterangan TEXT,

    CONSTRAINT fk_riwayat_makanan
        FOREIGN KEY (id_makanan)
        REFERENCES makanan(id_makanan)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT cek_jenis_transaksi
        CHECK (jenis_transaksi IN ('MASUK', 'KELUAR')),

    CONSTRAINT cek_jumlah
        CHECK (jumlah > 0)
);