import os
import streamlit as st
from google import genai
from google.genai import types

# ==========================================
# 1. KONFIGURASI HALAMAN & API KEY
# ==========================================
st.set_page_config(
    page_title="Belajar Bahasa Arab - Ustaz Izull", 
    page_icon="🕌",
    layout="wide"
)

# Ganti dengan API Key Gemini Anda jika tidak menggunakan Environment Variable
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "MASUKKAN_API_KEY_GEMINI_ANDA")

@st.cache_resource
def init_genai_client(api_key):
    try:
        return genai.Client(api_key=None if "MASUKKAN" in api_key else api_key)
    except Exception as e:
        st.error(f"Gagal inisialisasi Gemini Client: {e}")
        return None

client = init_genai_client(GEMINI_API_KEY)

# PROMPT SYSTEM INSTRUCTION (Sesuai Permintaan Anda)
SYSTEM_PROMPT = """
Anda adalah "Ustaz izull", seorang tutor AI yang ramah, berwibawa, dan suportif. Anda berperan sebagai teman praktik percakapan (Maharah kalam) bagi pelajar bahasa Arab tingkat Menengah, khususnya siswa MTS Kelas 8 di Indonesia.

Tujuan Utama Anda:
Membantu pengguna melatih keberanian, kelancaran, dan rasa percaya diri dalam berbicara teks bahasa Arab melalui simulasi yang realistis dan kontekstual.

Tugas dan Aturan Respons (WAJIB DIIKUTI SECARA KONSISTEN):
1. Format Bahasa: Tuliskan respons utama Anda menggunakan Bahasa Arab yang fasih dan wajib menyertakan HARAKAT lengkap agar mudah dibaca oleh siswa MTS Kelas 8. Tepat di bawah baris teks Arab tersebut, berikan terjemahan dalam Bahasa Indonesia (ditulis miring atau dalam tanda kurung) agar pengguna tetap memahami konteks alur percakapan.
2. Koreksi yang Lembut (Gentle Correction): Jika pengguna melakukan kesalahan tata bahasa (Nahwu/Sharaf), pilihan kata (diksi), atau struktur kalimat dalam percakapannya, JANGAN langsung menyalahkan atau memotong percakapan secara kaku. Berikan respons balasan yang benar terlebih dahulu dalam bahasa Arab yang natural. Kemudian, di bagian paling akhir pesan Anda, buatlah pembatas kecil bertuliskan "[Tips Ustaz]" dan jelaskan perbaikannya dengan bahasa Indonesia secara santun, edukatif, dan jelas.
3. Mendorong Partisipasi: Selalu akhiri setiap respons Anda dengan SATU pertanyaan terbuka yang relevan dalam bahasa Arab (beserta harakat dan terjemahannya) agar pembaca terus berlanjut dan tidak terputus.
4. Gaya Bahasa Pedagogis: Gunakan ungkapan-ungkapan ekspresif yang sering digunakan dalam percakapan nyata (seperti: 'Ya salam!', 'Tayyib', 'Masyaallah'). Berikan pujian yang tulus (seperti: 'Nutquka jayyid jiddan!' atau 'Mumtaz!') jika pengguna mencoba menggunakan kosakata baru dengan benar.

Mode/Topik Pembelajaran (Arahkan pengguna sesuai topik yang mereka pilih):
- Mode 1: Jam/Waktu  - Tata Bahasa: Penggunaan العدد الترتيby (Bilangan/Angka Urutan) dan kata tanya untuk waktu (MTS Kelas 8).
- Mode 2: Aktivitas Sehari-hari  - Membedakan dan menyusun الفِعْل المُضَارِع (Kata kerja bentuk sekarang/akan datang) beserta dhamir-nya.
- Mode 3: Al-Hiwayah (Hobi) - Penggunaan الجملة الفعلية (Kalimat yang diawali kata kerja) dan bentuk Mashdar Sharih.
"""

GREETING_MESSAGE = (
    "أَهْلًا وَسَهْلًا! أَنَا أُسْتَاذُ كَلَام، صَدِيقُكَ لِمُمَارَسَةِ الْمُحَادَثَةِ بِاللُّغَةِ الْعَرَبِيَّةِ لِتَكُونَ أَكْثَرَ طَلَاقَةً. "
    "اَلْيَوْمَ نُرِيدُ أَنْ نَتَدَرَّبَ عَلَى الْكَلَامِ، أَيْنَ نَتَدَرَّبُ؟ اِخْتَرِ الْمَوْضُوعَ:\n\n"
    "١. السَّاعَةُ (فِي الْمَدْرَسَةِ)\n"
    "٢. يَوْمِيَّاتُنَا\n"
    "٣. الْهِوَايَةُ (الْأَنْشِطَةُ فِي وَقْتِ الْفَرَاغِ)\n\n"
    "*(Ahlan wa Sahlan! Saya Ustaz Kalam, temanmu untuk melatih percakapan bahasa Arab agar lebih lancar. "
    "Hari ini kita mau latihan bicara di mana? Pilih topiknya ya:\n"
    "1. Jam/Waktu, 2. Aktivitas Sehari-hari, atau 3. Tentang Hobi)*"
)

# ==========================================
# 2. TAMPILAN BILAH SAMPING (SIDEBAR / FOLDER)
# ==========================================
st.sidebar.markdown("### 👤 Profil Pengguna")
with st.sidebar.container(border=True):
    st.markdown("**Nama:** Melisa")
    st.markdown("**Username:** @melisa_34")

st.sidebar.write("---")

st.sidebar.markdown("### 📁 Folder Navigasi")
menu_terpilih = st.sidebar.radio(
    label="Pilih Menu:",
    options=["📁 root/percobaan-kalam", "📁 root/panduan-belajar"],
    label_visibility="collapsed"
)

# ==========================================
# 3. INTERFACES & MANAJEMEN CHAT
# ==========================================
if "percobaan-kalam" in menu_terpilih:
    st.title("🕌 Kelas Kalam Bersama Ustaz Izull")
    st.write("Silakan pilih topik atau langsung jawab sapaan Ustaz di bawah menggunakan bahasa Arab!")

    # Inisialisasi riwayat pesan streamlit
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": GREETING_MESSAGE}]

    # Inisialisasi Objek Chat dari google-genai
    if "gemini_chat" not in st.session_state:
        if client:
            st.session_state.gemini_chat = client.chats.create(
                model="gemini-2.5-flash",
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.7,
                )
            )
        else:
            st.session_state.gemini_chat = None

    # Menampilkan riwayat percakapan di layar
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Input pengguna
    if user_input := st.chat_input("Tulis balasan bahasa Arab Anda di sini..."):
        # Tampilkan pesan pengguna
        st.chat_message("user").write(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})

        if st.session_state.gemini_chat is None:
            st.error("API Key belum diset dengan benar. Silakan cek baris kode nomor 13.")
        else:
            with st.spinner("Ustaz Izull sedang mengetik respons..."):
                try:
                    # Mengirim pesan ke sesi obrolan Gemini yang aktif
                    response = st.session_state.gemini_chat.send_message(user_input)
                    
                    # Tampilkan respons AI
                    with st.chat_message("assistant"):
                        st.markdown(response.text)
                    
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"Terjadi kesalahan: {e}")

else:
    # Halaman Panduan Belajar jika folder menu kedua diklik
    st.title("📖 Panduan Materi MTs Kelas 8")
    st.info("Gunakan ruang obrolan di menu sebelah kiri untuk mempraktikkan langsung tema-tema berikut:")
    st.markdown("""
    - **Tema 1 (Jam):** Fokus pada bilangan bertingkat (*al-adad at-tartibi*), contoh: السَّاعَةُ الْوَاحِدَةُ (Jam 1).
    - **Tema 2 (Keseharian):** Menggunakan kata kerja masa kini (*Fi'il Mudhari'*), contoh: أَذْهَبُ (Saya pergi), تَقْرَأُ (Kamu membaca).
    - **Tema 3 (Hobi):** Mengenal hobi (*Al-Hiwayah*), contoh: الرَّسْمُ (Melukis), الْقِرَاءَةُ (Membaca).
    """)