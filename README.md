# 🕌 Zakat & Wakaf Audit AI

Sistem audit kepatuhan syariah berbasis **Python** dan **Streamlit** untuk membantu Lembaga Amil Zakat (LAZ) dan Dewan Kemakmuran Masjid (DKM) memverifikasi kesesuaian penyaluran zakat terhadap **8 Asnaf** serta melacak transparansi aset **Wakaf**.

## ✨ Fitur Utama
1. **Verifikasi 8 Asnaf Otomatis:** Memastikan seluruh penyaluran zakat hanya ditujukan kepada *Fakir, Miskin, Amil, Muallaf, Riqab, Gharimin, Fisabilillah,* dan *Ibnu Sabil*.
2. **Deteksi Belanja Fisik Non-Zakat (AI Keyword Analyzer):** Mendeteksi transaksi dana zakat yang digunakan untuk renovasi/pembangunan fisik (misalnya pembelian semen, cat, pagar) yang seharusnya menggunakan dana Infak atau Sedekah.
3. **Kontrol Rasio Hak Amil:** Menghitung proporsi pengambilan hak amil secara otomatis dan memberi peringatan jika melebihi batas syariah **12,5% (1/8)**.
4. **Deteksi Anomali Penerima:** Menandai pencairan ganda kepada ID/NIK mustahik yang sama dalam satu periode laporan.
5. **Transparansi Aset Wakaf:** Memantau keutuhan nilai pokok aset wakaf (*Mauquf*) serta arus kas hasil wakaf produktif kepada penerima manfaat (*Mauquf 'Alaih*).
6. **Ekspor Laporan Audit (.xlsx):** Mengunduh kertas kerja hasil audit lengkap dengan catatan temuan AI.

## 📁 Struktur Proyek
```text
zakat-wakaf-audit-ai/
├── app.py              # Antarmuka aplikasi Streamlit (3 Tab)
├── audit_engine.py     # Logika kepatuhan syariah & deteksi anomali
├── sample_data.csv     # Dataset simulasi transaksi Zakat & Wakaf
├── requirements.txt    # Daftar pustaka Python
└── README.md           # Dokumentasi proyek
