
from app.extensions import db


class Kategori(db.Model):
    __tablename__ = "kategori"

    id_kategori = db.Column(db.Integer, primary_key=True)
    nama_kategori = db.Column(db.String(100), nullable=False)
    deskripsi = db.Column(db.Text)


class LokasiPenyimpanan(db.Model):
    __tablename__ = "lokasi_penyimpanan"

    id_lokasi = db.Column(db.Integer, primary_key=True)
    nama_lokasi = db.Column(db.String(100), nullable=False)
    keterangan = db.Column(db.Text)


class Makanan(db.Model):
    __tablename__ = "makanan"

    id_makanan = db.Column(db.Integer, primary_key=True)
    nama_makanan = db.Column(db.String(150), nullable=False)
    id_kategori = db.Column(
        db.Integer,
        db.ForeignKey("kategori.id_kategori"),
        nullable=False
    )
    id_lokasi = db.Column(
        db.Integer,
        db.ForeignKey("lokasi_penyimpanan.id_lokasi"),
        nullable=False
    )
    satuan = db.Column(db.String(30), nullable=False)
    tanggal_kedaluwarsa = db.Column(db.Date)


class Stok(db.Model):
    __tablename__ = "stok"

    id_stok = db.Column(db.Integer, primary_key=True)
    id_makanan = db.Column(
        db.Integer,
        db.ForeignKey("makanan.id_makanan"),
        nullable=False,
        unique=True
    )
    jumlah_stok = db.Column(db.Integer, nullable=False, default=0)
    stok_minimum = db.Column(db.Integer, nullable=False, default=0)
    tanggal_update = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp()
    )


class RiwayatStok(db.Model):
    __tablename__ = "riwayat_stok"

    id_riwayat = db.Column(db.Integer, primary_key=True)
    id_makanan = db.Column(
        db.Integer,
        db.ForeignKey("makanan.id_makanan"),
        nullable=False
    )
    jenis_transaksi = db.Column(db.String(10), nullable=False)
    jumlah = db.Column(db.Integer, nullable=False)
    tanggal_transaksi = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp()
    )
    keterangan = db.Column(db.Text)
