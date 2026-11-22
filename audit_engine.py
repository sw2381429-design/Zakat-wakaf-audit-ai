import pandas as pd

ASNAF_RESMI = [
    "Fakir", "Miskin", "Amil", "Muallaf",
    "Riqab", "Gharimin", "Fisabilillah", "Ibnu Sabil"
]

# Kata kunci pengeluaran fisik/infrastruktur yang dilarang memakai dana Zakat
KATA_KUNCI_NON_ZAKAT = [
    "semen", "cat", "renovasi", "pagar", "kanopi", "keramik",
    "bangunan", "sound system", "karpet", "ac masjid", "listrik masjid"
]


def run_zakat_audit(df: pd.DataFrame) -> dict:
    """Melakukan audit kepatuhan syariah pada transaksi Zakat."""
    df_zakat = df[df["jenis_dana"].str.lower() == "zakat"].copy()

    total_masuk = df_zakat["masuk"].sum()
    total_keluar = df_zakat["keluar"].sum()

    # Hitung hak Amil (maksimal syariah 1/8 = 12.5%)
    keluar_amil = df_zakat[df_zakat["kategori"].str.lower() == "amil"]["keluar"].sum()
    rasio_amil = (keluar_amil / total_masuk * 100) if total_masuk > 0 else 0.0
    status_amil = "PATUH (<= 12.5%)" if rasio_amil <= 12.5 else "MELEBIHI BATAS (> 12.5%)"

    # Audit per baris transaksi pengeluaran zakat
    df_salur = df_zakat[df_zakat["keluar"] > 0].copy()
    nik_counts = df_salur["nik_id"].value_counts()

    hasil_status = []
    catatan_audit = []

    for _, row in df_salur.iterrows():
        masalah = []
        kategori = str(row["kategori"]).strip()
        ket = str(row["keterangan"]).lower()
        nik = row["nik_id"]

        # 1. Cek kategori 8 Asnaf
        if kategori not in ASNAF_RESMI:
            masalah.append(f"Kategori '{kategori}' bukan termasuk 8 Asnaf")

        # 2. AI NLP Rule: Cek penyalahgunaan dana zakat untuk fisik bangunan
        kata_terdeteksi = [k for k in KATA_KUNCI_NON_ZAKAT if k in ket]
        if kata_terdeteksi:
            masalah.append(
                f"Terdeteksi belanja fisik ({', '.join(kata_terdeteksi)}) — seharusnya memakai dana Infak/Sedekah"
            )

        # 3. Deteksi Anomali: Penerima ganda dalam satu periode
        if nik_counts.get(nik, 0) > 1 and kategori.lower() != "amil":
            masalah.append(f"Anomali: ID/NIK ({nik}) menerima penyaluran lebih dari 1 kali")

        if masalah:
            hasil_status.append("FLAGGED (Perlu Klarifikasi)")
            catatan_audit.append(" | ".join(masalah))
        else:
            hasil_status.append("SESUAI SYARIAH")
            catatan_audit.append("Memenuhi kriteria Asnaf & kewajaran transaksi")

    df_salur["Status_Audit"] = hasil_status
    df_salur["Catatan_AI"] = catatan_audit

    jumlah_flagged = (df_salur["Status_Audit"] != "SESUAI SYARIAH").sum()
    total_salur_tx = len(df_salur)

    # Hitung Skor Kepatuhan Syariah (0 - 100)
    skor_tx = ((total_salur_tx - jumlah_flagged) / total_salur_tx * 80) if total_salur_tx > 0 else 80
    skor_amil = 20 if rasio_amil <= 12.5 else max(0, 20 - (rasio_amil - 12.5) * 2)
    skor_total = round(skor_tx + skor_amil, 1)

    return {
        "df_salur": df_salur,
        "total_masuk": total_masuk,
        "total_keluar": total_keluar,
        "keluar_amil": keluar_amil,
        "rasio_amil": round(rasio_amil, 2),
        "status_amil": status_amil,
        "jumlah_flagged": int(jumlah_flagged),
        "skor_syariah": skor_total,
    }


def run_wakaf_audit(df: pd.DataFrame) -> dict:
    """Melakukan audit transparansi aset dan hasil pengelolaan wakaf."""
    df_wakaf = df[df["jenis_dana"].str.lower() == "wakaf"].copy()

    if df_wakaf.empty:
        return {
            "df_wakaf": df_wakaf,
            "nilai_pokok_awal": 0,
            "nilai_pokok_akhir": 0,
            "status_pokok": "Tidak ada data wakaf",
            "hasil_wakaf_masuk": 0,
            "hasil_wakaf_salur": 0,
            "saldo_hasil_wakaf": 0,
        }

    nilai_pokok_awal = df_wakaf["nilai_pokok_wakaf"].iloc[0]
    nilai_pokok_akhir = df_wakaf["nilai_pokok_wakaf"].iloc[-1]

    # Prinsip utama wakaf: nilai pokok tidak boleh menyusut
    if nilai_pokok_akhir >= nilai_pokok_awal:
        status_pokok = "TERJAGA (Nilai pokok utuh/bertambah)"
    else:
        status_pokok = "PERINGATAN: Nilai pokok aset wakaf menyusut!"

    hasil_masuk = df_wakaf["masuk"].sum()
    hasil_salur = df_wakaf["keluar"].sum()
    saldo_hasil = hasil_masuk - hasil_salur

    return {
        "df_wakaf": df_wakaf,
        "nilai_pokok_awal": nilai_pokok_awal,
        "nilai_pokok_akhir": nilai_pokok_akhir,
        "status_pokok": status_pokok,
        "hasil_wakaf_masuk": hasil_masuk,
        "hasil_wakaf_salur": hasil_salur,
        "saldo_hasil_wakaf": saldo_hasil,
    }
