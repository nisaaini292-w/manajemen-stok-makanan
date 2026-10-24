import os
from datetime import date, datetime

from flask import Flask, jsonify, request
from dotenv import load_dotenv

from app.extensions import db
from app.models import Kategori, LokasiPenyimpanan, Makanan, Stok, RiwayatStok


def create_app():
    load_dotenv()

    app = Flask(__name__)

    database_url = os.getenv("DATABASE_URL")

    # Paksa memakai driver psycopg2, apa pun awalan URL-nya
    if database_url and "://" in database_url:
        database_url = "postgresql+psycopg2://" + database_url.split("://", 1)[1]

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_pre_ping": True}

    db.init_app(app)

    # =========================
    # HALAMAN UTAMA
    # =========================

    @app.route("/", methods=["GET"])
    def home():
        return jsonify({
            "status": "success",
            "message": "API Manajemen Stok Makanan berjalan"
        }), 200

    @app.route("/db-check", methods=["GET"])
    def db_check():
        try:
            db.session.execute(db.text("SELECT 1"))
            return jsonify({
                "status": "success",
                "message": "Database berhasil terhubung"
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({
                "status": "error",
                "message": "Database gagal terhubung",
                "detail": str(e)
            }), 500

    # =========================
    # FUNGSI BANTUAN
    # =========================

    def error_response(message, status_code=400):
        return jsonify({
            "status": "error",
            "message": message
        }), status_code

    def parse_integer(value, field_name):
        try:
            if isinstance(value, bool) or value is None:
                raise ValueError
            return int(value)
        except (ValueError, TypeError):
            raise ValueError(f"{field_name} harus berupa bilangan bulat")

    def parse_date(value):
        if value in (None, ""):
            return None
        try:
            return date.fromisoformat(value)
        except (ValueError, TypeError):
            raise ValueError("Format tanggal harus YYYY-MM-DD")

    def makanan_to_dict(makanan):
        return {
            "id_makanan": makanan.id_makanan,
            "nama_makanan": makanan.nama_makanan,
            "id_kategori": makanan.id_kategori,
            "id_lokasi": makanan.id_lokasi,
            "satuan": makanan.satuan,
            "tanggal_kedaluwarsa": (
                makanan.tanggal_kedaluwarsa.isoformat()
                if makanan.tanggal_kedaluwarsa else None
            )
        }

    def stok_to_dict(stok):
        return {
            "id_stok": stok.id_stok,
            "id_makanan": stok.id_makanan,
            "jumlah_stok": stok.jumlah_stok,
            "stok_minimum": stok.stok_minimum,
            "tanggal_update": (
                stok.tanggal_update.isoformat()
                if stok.tanggal_update else None
            )
        }

    def riwayat_to_dict(riwayat):
        return {
            "id_riwayat": riwayat.id_riwayat,
            "id_makanan": riwayat.id_makanan,
            "jenis_transaksi": riwayat.jenis_transaksi,
            "jumlah": riwayat.jumlah,
            "tanggal_transaksi": (
                riwayat.tanggal_transaksi.isoformat()
                if riwayat.tanggal_transaksi else None
            ),
            "keterangan": riwayat.keterangan
        }

    # =========================
    # CRUD MAKANAN
    # =========================

    @app.route("/makanan", methods=["GET"])
    def get_makanan():
        data = Makanan.query.order_by(Makanan.id_makanan).all()

        return jsonify({
            "status": "success",
            "data": [makanan_to_dict(item) for item in data]
        }), 200

    @app.route("/makanan/<int:id_makanan>", methods=["GET"])
    def get_makanan_detail(id_makanan):
        makanan = db.session.get(Makanan, id_makanan)

        if not makanan:
            return error_response("Data makanan tidak ditemukan", 404)

        return jsonify({
            "status": "success",
            "data": makanan_to_dict(makanan)
        }), 200

    @app.route("/makanan", methods=["POST"])
    def tambah_makanan():
        data = request.get_json(silent=True) or {}

        nama = data.get("nama_makanan")
        satuan = data.get("satuan")
        id_kategori = data.get("id_kategori")
        id_lokasi = data.get("id_lokasi")

        if not nama or not satuan:
            return error_response(
                "nama_makanan dan satuan wajib diisi"
            )

        try:
            id_kategori = parse_integer(id_kategori, "id_kategori")
            id_lokasi = parse_integer(id_lokasi, "id_lokasi")
            tanggal = parse_date(data.get("tanggal_kedaluwarsa"))

            if not db.session.get(Kategori, id_kategori):
                return error_response("Kategori tidak ditemukan", 404)

            if not db.session.get(LokasiPenyimpanan, id_lokasi):
                return error_response(
                    "Lokasi penyimpanan tidak ditemukan", 404
                )

            makanan = Makanan(
                nama_makanan=nama,
                id_kategori=id_kategori,
                id_lokasi=id_lokasi,
                satuan=satuan,
                tanggal_kedaluwarsa=tanggal
            )

            db.session.add(makanan)
            db.session.flush()

            stok = Stok(
                id_makanan=makanan.id_makanan,
                jumlah_stok=0,
                stok_minimum=0
            )

            db.session.add(stok)
            db.session.commit()

            return jsonify({
                "status": "success",
                "message": "Makanan berhasil ditambahkan",
                "data": makanan_to_dict(makanan)
            }), 201

        except ValueError as e:
            db.session.rollback()
            return error_response(str(e))

        except Exception:
            db.session.rollback()
            app.logger.exception("Gagal menambahkan makanan")
            return error_response(
                "Gagal menambahkan makanan. Periksa data yang dikirim.",
                500
            )

    @app.route("/makanan/<int:id_makanan>", methods=["PUT"])
    def ubah_makanan(id_makanan):
        makanan = db.session.get(Makanan, id_makanan)

        if not makanan:
            return error_response("Data makanan tidak ditemukan", 404)

        data = request.get_json(silent=True) or {}

        try:
            if "nama_makanan" in data:
                if not data["nama_makanan"]:
                    return error_response("Nama makanan tidak boleh kosong")
                makanan.nama_makanan = data["nama_makanan"]

            if "satuan" in data:
                if not data["satuan"]:
                    return error_response("Satuan tidak boleh kosong")
                makanan.satuan = data["satuan"]

            if "id_kategori" in data:
                nilai = parse_integer(data["id_kategori"], "id_kategori")
                if not db.session.get(Kategori, nilai):
                    return error_response("Kategori tidak ditemukan", 404)
                makanan.id_kategori = nilai

            if "id_lokasi" in data:
                nilai = parse_integer(data["id_lokasi"], "id_lokasi")
                if not db.session.get(LokasiPenyimpanan, nilai):
                    return error_response(
                        "Lokasi penyimpanan tidak ditemukan", 404
                    )
                makanan.id_lokasi = nilai

            if "tanggal_kedaluwarsa" in data:
                makanan.tanggal_kedaluwarsa = parse_date(
                    data["tanggal_kedaluwarsa"]
                )

            db.session.commit()

            return jsonify({
                "status": "success",
                "message": "Data makanan berhasil diperbarui",
                "data": makanan_to_dict(makanan)
            }), 200

        except ValueError as e:
            db.session.rollback()
            return error_response(str(e))

        except Exception:
            db.session.rollback()
            app.logger.exception("Gagal memperbarui makanan")
            return error_response("Gagal memperbarui makanan", 500)

    @app.route("/makanan/<int:id_makanan>", methods=["DELETE"])
    def hapus_makanan(id_makanan):
        makanan = db.session.get(Makanan, id_makanan)

        if not makanan:
            return error_response("Data makanan tidak ditemukan", 404)

        riwayat = RiwayatStok.query.filter_by(
            id_makanan=id_makanan
        ).first()

        if riwayat:
            return error_response(
                "Makanan memiliki riwayat transaksi sehingga tidak dapat dihapus",
                409
            )

        try:
            stok = Stok.query.filter_by(id_makanan=id_makanan).first()

            if stok:
                db.session.delete(stok)

            db.session.delete(makanan)
            db.session.commit()

            return jsonify({
                "status": "success",
                "message": "Makanan berhasil dihapus"
            }), 200

        except Exception:
            db.session.rollback()
            app.logger.exception("Gagal menghapus makanan")
            return error_response("Gagal menghapus makanan", 500)

    # =========================
    # CRUD STOK
    # =========================

    @app.route("/stok", methods=["GET"])
    def get_stok():
        data = Stok.query.order_by(Stok.id_stok).all()

        return jsonify({
            "status": "success",
            "data": [stok_to_dict(item) for item in data]
        }), 200

    @app.route("/stok/<int:id_stok>", methods=["GET"])
    def get_stok_detail(id_stok):
        stok = db.session.get(Stok, id_stok)

        if not stok:
            return error_response("Data stok tidak ditemukan", 404)

        return jsonify({
            "status": "success",
            "data": stok_to_dict(stok)
        }), 200

    @app.route("/stok", methods=["POST"])
    def tambah_stok():
        data = request.get_json(silent=True) or {}

        try:
            id_makanan = parse_integer(
                data.get("id_makanan"), "id_makanan"
            )
            jumlah = parse_integer(
                data.get("jumlah_stok", 0), "jumlah_stok"
            )
            minimum = parse_integer(
                data.get("stok_minimum", 0), "stok_minimum"
            )

            if jumlah < 0 or minimum < 0:
                return error_response("Jumlah stok tidak boleh negatif")

            if not db.session.get(Makanan, id_makanan):
                return error_response("Makanan tidak ditemukan", 404)

            stok_lama = Stok.query.filter_by(
                id_makanan=id_makanan
            ).first()

            if stok_lama:
                return error_response(
                    "Stok untuk makanan ini sudah tersedia. Gunakan PUT untuk memperbaruinya.",
                    409
                )

            stok = Stok(
                id_makanan=id_makanan,
                jumlah_stok=jumlah,
                stok_minimum=minimum
            )

            db.session.add(stok)
            db.session.commit()

            return jsonify({
                "status": "success",
                "message": "Data stok berhasil ditambahkan",
                "data": stok_to_dict(stok)
            }), 201

        except ValueError as e:
            db.session.rollback()
            return error_response(str(e))

        except Exception:
            db.session.rollback()
            app.logger.exception("Gagal menambahkan stok")
            return error_response("Gagal menambahkan stok", 500)

    @app.route("/stok/<int:id_stok>", methods=["PUT"])
    def ubah_stok(id_stok):
        stok = db.session.get(Stok, id_stok)

        if not stok:
            return error_response("Data stok tidak ditemukan", 404)

        data = request.get_json(silent=True) or {}

        try:
            if "jumlah_stok" in data:
                jumlah = parse_integer(
                    data["jumlah_stok"], "jumlah_stok"
                )
                if jumlah < 0:
                    return error_response("Jumlah stok tidak boleh negatif")
                stok.jumlah_stok = jumlah

            if "stok_minimum" in data:
                minimum = parse_integer(
                    data["stok_minimum"], "stok_minimum"
                )
                if minimum < 0:
                    return error_response("Stok minimum tidak boleh negatif")
                stok.stok_minimum = minimum

            stok.tanggal_update = datetime.now()
            db.session.commit()

            return jsonify({
                "status": "success",
                "message": "Data stok berhasil diperbarui",
                "data": stok_to_dict(stok)
            }), 200

        except ValueError as e:
            db.session.rollback()
            return error_response(str(e))

        except Exception:
            db.session.rollback()
            app.logger.exception("Gagal memperbarui stok")
            return error_response("Gagal memperbarui stok", 500)

    @app.route("/stok/<int:id_stok>", methods=["DELETE"])
    def hapus_stok(id_stok):
        stok = db.session.get(Stok, id_stok)

        if not stok:
            return error_response("Data stok tidak ditemukan", 404)

        riwayat = RiwayatStok.query.filter_by(
            id_makanan=stok.id_makanan
        ).first()

        if riwayat:
            return error_response(
                "Stok memiliki riwayat transaksi sehingga tidak dapat dihapus",
                409
            )

        try:
            db.session.delete(stok)
            db.session.commit()

            return jsonify({
                "status": "success",
                "message": "Data stok berhasil dihapus"
            }), 200

        except Exception:
            db.session.rollback()
            app.logger.exception("Gagal menghapus stok")
            return error_response("Gagal menghapus stok", 500)

    # =========================
    # RIWAYAT TRANSAKSI STOK
    # =========================

    @app.route("/riwayat-stok", methods=["GET"])
    def get_riwayat_stok():
        data = RiwayatStok.query.order_by(
            RiwayatStok.id_riwayat.desc()
        ).all()

        return jsonify({
            "status": "success",
            "data": [riwayat_to_dict(item) for item in data]
        }), 200

    @app.route("/riwayat-stok/<int:id_riwayat>", methods=["GET"])
    def get_riwayat_detail(id_riwayat):
        riwayat = db.session.get(RiwayatStok, id_riwayat)

        if not riwayat:
            return error_response("Riwayat transaksi tidak ditemukan", 404)

        return jsonify({
            "status": "success",
            "data": riwayat_to_dict(riwayat)
        }), 200

    @app.route("/riwayat-stok", methods=["POST"])
    def tambah_riwayat_stok():
        data = request.get_json(silent=True) or {}

        try:
            id_makanan = parse_integer(
                data.get("id_makanan"), "id_makanan"
            )
            jumlah = parse_integer(data.get("jumlah"), "jumlah")
            jenis = str(data.get("jenis_transaksi", "")).strip().upper()
            keterangan = data.get("keterangan")

            if jenis not in ("MASUK", "KELUAR"):
                return error_response(
                    "jenis_transaksi harus MASUK atau KELUAR"
                )

            if jumlah <= 0:
                return error_response("Jumlah transaksi harus lebih dari 0")

            makanan = db.session.get(Makanan, id_makanan)

            if not makanan:
                return error_response("Makanan tidak ditemukan", 404)

            stok = Stok.query.filter_by(
                id_makanan=id_makanan
            ).with_for_update().first()

            if not stok:
                return error_response(
                    "Data stok untuk makanan ini belum tersedia",
                    404
                )

            if jenis == "KELUAR" and stok.jumlah_stok < jumlah:
                return error_response(
                    "Stok tidak mencukupi untuk transaksi keluar"
                )

            if jenis == "MASUK":
                stok.jumlah_stok += jumlah
            else:
                stok.jumlah_stok -= jumlah

            stok.tanggal_update = datetime.now()

            riwayat = RiwayatStok(
                id_makanan=id_makanan,
                jenis_transaksi=jenis,
                jumlah=jumlah,
                keterangan=keterangan
            )

            db.session.add(riwayat)
            db.session.commit()

            return jsonify({
                "status": "success",
                "message": "Transaksi stok berhasil dicatat",
                "data": {
                    "riwayat": riwayat_to_dict(riwayat),
                    "stok_sekarang": stok_to_dict(stok)
                }
            }), 201

        except ValueError as e:
            db.session.rollback()
            return error_response(str(e))

        except Exception:
            db.session.rollback()
            app.logger.exception("Gagal mencatat transaksi stok")
            return error_response(
                "Gagal mencatat transaksi stok. Periksa terminal Flask untuk detailnya.",
                500
            )

    @app.route("/riwayat-stok/<int:id_riwayat>", methods=["PUT"])
    def ubah_riwayat_stok(id_riwayat):
        riwayat = db.session.get(RiwayatStok, id_riwayat)

        if not riwayat:
            return error_response("Riwayat transaksi tidak ditemukan", 404)

        data = request.get_json(silent=True) or {}

        if "keterangan" not in data:
            return error_response(
                "Hanya kolom keterangan yang dapat diperbarui"
            )

        try:
            riwayat.keterangan = data["keterangan"]
            db.session.commit()

            return jsonify({
                "status": "success",
                "message": "Keterangan riwayat berhasil diperbarui",
                "data": riwayat_to_dict(riwayat)
            }), 200

        except Exception:
            db.session.rollback()
            app.logger.exception("Gagal memperbarui riwayat")
            return error_response("Gagal memperbarui riwayat", 500)

    @app.route("/riwayat-stok/<int:id_riwayat>", methods=["DELETE"])
    def hapus_riwayat_stok(id_riwayat):
        riwayat = db.session.get(RiwayatStok, id_riwayat)

        if not riwayat:
            return error_response("Riwayat transaksi tidak ditemukan", 404)

        return error_response(
            "Riwayat transaksi tidak dapat dihapus agar catatan stok tetap akurat",
            409
        )

    return app
