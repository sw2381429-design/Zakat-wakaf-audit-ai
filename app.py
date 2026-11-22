import io
import pandas as pd
import plotly.express as px
import streamlit as st
from audit_engine import run_zakat_audit, run_wakaf_audit

st.set_page_config(
    page_title="Zakat & Wakaf Audit AI",
    page_icon="🕌",
    layout="wide"
)

st.title("🕌 Zakat & Wakaf Audit AI")
st.caption("Sistem Verifikasi Kepatuhan 8 Asnaf & Transparansi Pengelolaan Aset Wakaf")

# --- PANDUAN PENGGUNAAN SINGKAT ---
with st.expander("📖 Panduan Penggunaan Singkat (Klik untuk membuka)", expanded=False):
    g1, g2, g3 = st.columns(3)
    with g1:
        st.markdown("**1️⃣ Pilih atau Unduh Data**")
        st.write(
            "Gunakan **Data Uji Coba** yang sudah tersedia di dashboard untuk melihat simulasi audit, "
            "atau unduh format `.csv` sampel lalu isi dengan mutasi kas masjid/LAZ Anda."
        )
    with g2:
        st.markdown("**2️⃣ Unggah & Audit Otomatis**")
        st.write(
            "Unggah file CSV/Excel melalui menu di sebelah kiri. Sistem AI akan otomatis mengecek "
            "kesesuaian **8 Asnaf**, batas hak **Amil (≤ 12,5%)**, dan keutuhan pokok **Wakaf**."
        )
    with g3:
        st.markdown("**3️⃣ Tinjau & Unduh Laporan**")
        st.write(
            "Periksa transaksi bertanda merah (*FLAGGED*) di Tab Zakat & Wakaf, lalu unduh "
            "**Kertas Kerja Hasil Audit (.xlsx)** di Tab 3 untuk laporan Dewan Pengawas Syariah."
        )

# --- DATA SAMPEL KEDUA (SKENARIO PATUH 100%) ---
def get_compliant_sample_df() -> pd.DataFrame:
    data = [
        ["2026-02-02", "Zakat", "Penghimpunan", "Muzakki Hamba Allah A", "MZ-101", "Zakat mal tahunan perusahaan", 20000000, 0, 0],
        ["2026-02-05", "Zakat", "Fakir", "Ibu Aminah", "32010101", "Santunan biaya hidup bulanan lansia", 0, 3000000, 0],
        ["2026-02-08", "Zakat", "Miskin", "Bapak Hasan", "32010102", "Bantuan gerobak dan modal dagang", 0, 4000000, 0],
        ["2026-02-12", "Zakat", "Gharimin", "Ibu Fatimah", "32010103", "Pelunasan tunggakan biaya berobat rumah sakit", 0, 3500000, 0],
        ["2026-02-15", "Zakat", "Ibnu Sabil", "Musafir Kehabisan Bekal", "32010104", "Bantuan tiket pulang ke kampung halaman", 0, 1000000, 0],
        ["2026-02-18", "Zakat", "Amil", "Pengurus UPZ Masjid", "AM-01", "Operasional penyaluran zakat bulan Februari", 0, 2000000, 0],
        ["2026-02-20", "Wakaf", "Aset Wakaf Uang", "Wakif H. Abdullah", "WK-101", "Sertifikat Wakaf Uang Abadi (SWU No. 05/2026)", 0, 0, 100000000],
        ["2026-02-25", "Wakaf", "Hasil Wakaf", "Bank Syariah Mitra", "WK-101", "Bagi hasil deposito wakaf uang", 1500000, 0, 100000000],
        ["2026-02-27", "Wakaf", "Mauquf Alaih", "Klinik Dhuafa Masjid", "KL-01", "Pengadaan obat gratis untuk dhuafa dari hasil wakaf", 0, 1500000, 100000000],
    ]
    cols = ["tanggal", "jenis_dana", "kategori", "penerima", "nik_id", "keterangan", "masuk", "keluar", "nilai_pokok_wakaf"]
    return pd.DataFrame(data, columns=cols)

# --- SIDEBAR: SUMBER DATA ---
with st.sidebar:
    st.header("📂 Sumber Data Keuangan")
    sumber = st.radio(
        "Pilih Sumber Data:",
        ["Mode Uji Coba (Data Sampel)", "Unggah File Sendiri (.csv / .xlsx)"]
    )

    df = None
    if sumber == "Unggah File Sendiri (.csv / .xlsx)":
        uploaded_file = st.file_uploader("Unggah Mutasi Kas", type=["csv", "xlsx"])
        if uploaded_file:
            df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
            st.success(f"File '{uploaded_file.name}' berhasil dimuat!")

# --- PANEL UJI COBA & DOWNLOAD SAMPEL DI DASHBOARD ---
if sumber == "Mode Uji Coba (Data Sampel)":
    with st.container(border=True):
        st.subheader("🧪 Panel Uji Coba Instan & Download Data Sampel")
        col_pilih, col_dl1, col_dl2 = st.columns([2, 1, 1])

        with col_pilih:
            skenario = st.selectbox(
                "Pilih Skenario Data Uji Coba:",
                [
                    "Skenario A: Terdapat Pelanggaran Asnaf & Anomali (Default)",
                    "Skenario B: Laporan Bersih & 100% Patuh Syariah"
                ]
            )

        df_skenario_a = pd.read_csv("sample_data.csv")
        df_skenario_b = get_compliant_sample_df()

        with col_dl1:
            st.write("")
            st.download_button(
                label="📥 Unduh Sampel A (Ada Temuan)",
                data=df_skenario_a.to_csv(index=False).encode("utf-8"),
                file_name="sampel_audit_temuan.csv",
                mime="text/csv",
                use_container_width=True
            )

        with col_dl2:
            st.write("")
            st.download_button(
                label="📥 Unduh Sampel B (Patuh 100%)",
                data=df_skenario_b.to_csv(index=False).encode("utf-8"),
                file_name="sampel_audit_patuh.csv",
                mime="text/csv",
                use_container_width=True
            )

        df = df_skenario_a if "Skenario A" in skenario else df_skenario_b

if df is None:
    st.info("👈 Silakan unggah file CSV/Excel Anda di panel sebelah kiri, atau beralih ke **Mode Uji Coba (Data Sampel)**.")
    st.stop()

# Jalankan mesin audit
hasil_zakat = run_zakat_audit(df)
hasil_wakaf = run_wakaf_audit(df)

# --- 3 TAB UTAMA ---
tab1, tab2, tab3 = st.tabs([
    "📊 Audit Penyaluran Zakat",
    "🏛️ Transparansi Aset Wakaf",
    "📑 Ringkasan & Ekspor Laporan"
])

# === TAB 1: AUDIT ZAKAT ===
with tab1:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Zakat Masuk", f"Rp {hasil_zakat['total_masuk']:,.0f}")
    c2.metric("Total Zakat Tersalurkan", f"Rp {hasil_zakat['total_keluar']:,.0f}")
    c3.metric(
        "Rasio Hak Amil (Batas 12.5%)",
        f"{hasil_zakat['rasio_amil']}%",
        hasil_zakat["status_amil"],
        delta_color="normal" if hasil_zakat["rasio_amil"] <= 12.5 else "inverse"
    )
    c4.metric(
        "Transaksi Terdeteksi Anomali",
        f"{hasil_zakat['jumlah_flagged']} Transaksi",
        "Perlu Tinjauan" if hasil_zakat["jumlah_flagged"] > 0 else "Aman",
        delta_color="inverse" if hasil_zakat["jumlah_flagged"] > 0 else "normal"
    )

    st.divider()
    col_chart, col_table = st.columns([1, 2])

    with col_chart:
        st.subheader("Distribusi per Asnaf")
        df_salur = hasil_zakat["df_salur"]
        if not df_salur.empty:
            fig = px.pie(
                df_salur,
                names="kategori",
                values="keluar",
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig.update_layout(margin=dict(t=20, b=20, l=10, r=10))
            st.plotly_chart(fig, use_container_width=True)

    with col_table:
        st.subheader("Hasil Verifikasi AI per Transaksi")
        st.dataframe(
            df_salur[["tanggal", "kategori", "penerima", "keterangan", "keluar", "Status_Audit", "Catatan_AI"]],
            use_container_width=True,
            hide_index=True
        )

# === TAB 2: AUDIT WAKAF ===
with tab2:
    w1, w2, w3 = st.columns(3)
    w1.metric(
        "Nilai Pokok Aset Wakaf",
        f"Rp {hasil_wakaf['nilai_pokok_akhir']:,.0f}",
        hasil_wakaf["status_pokok"]
    )
    w2.metric("Hasil Wakaf Produktif (Masuk)", f"Rp {hasil_wakaf['hasil_wakaf_masuk']:,.0f}")
    w3.metric("Penyaluran Mauquf 'Alaih", f"Rp {hasil_wakaf['hasil_wakaf_salur']:,.0f}")

    st.divider()
    st.subheader("Riwayat Aset & Arus Kas Pengelolaan Wakaf")
    if not hasil_wakaf["df_wakaf"].empty:
        st.dataframe(
            hasil_wakaf["df_wakaf"][["tanggal", "kategori", "penerima", "keterangan", "masuk", "keluar", "nilai_pokok_wakaf"]],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("Belum ada transaksi berkategori 'Wakaf' pada dataset yang diunggah.")

# === TAB 3: LAPORAN SYARIAH ===
with tab3:
    st.subheader("Skor Kepatuhan Syariah Lembaga")
    skor = hasil_zakat["skor_syariah"]
    st.progress(int(skor) / 100)
    st.markdown(f"### Skor Audit: **{skor} / 100**")

    if hasil_zakat["rasio_amil"] > 12.5:
        st.error(f"⚠️ **Temuan Amil:** Alokasi amil mencapai {hasil_zakat['rasio_amil']}%, melebihi batas wajar syariah 12,5% (1/8).")
    if hasil_zakat["jumlah_flagged"] > 0:
        st.warning(f"⚠️ **Temuan Penyaluran:** Ditemukan {hasil_zakat['jumlah_flagged']} transaksi yang memerlukan klarifikasi Dewan Pengawas Syariah.")
    if hasil_zakat["rasio_amil"] <= 12.5 and hasil_zakat["jumlah_flagged"] == 0:
        st.success("✅ Seluruh transaksi zakat dan rasio amil telah sesuai dengan ketentuan syariah.")

    # Ekspor ke Excel
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        hasil_zakat["df_salur"].to_excel(writer, sheet_name="Audit_Zakat", index=False)
        if not hasil_wakaf["df_wakaf"].empty:
            hasil_wakaf["df_wakaf"].to_excel(writer, sheet_name="Audit_Wakaf", index=False)

    st.download_button(
        label="📥 Unduh Laporan Hasil Audit Lengkap (.xlsx)",
        data=buffer.getvalue(),
        file_name="Laporan_Audit_Syariah_Zakat_Wakaf.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
