import streamlit as st
import pandas as pd
import io
from fpdf import FPDF
import zipfile
import os
import math

def turkce_sirala_anahtar(metin):
    turkce_harf_agirliklari = {
        'a': 1, 'b': 2, 'c': 3, 'ç': 4, 'd': 5, 'e': 6, 'f': 7, 'g': 8, 'ğ': 9, 'h': 10,
        'ı': 11, 'i': 12, 'j': 13, 'k': 14, 'l': 15, 'm': 16, 'n': 17, 'o': 18, 'ö': 19,
        'p': 20, 'r': 21, 's': 22, 'ş': 23, 't': 24, 'u': 25, 'ü': 26, 'v': 27, 'y': 28, 'z': 29,
        'A': 1, 'B': 2, 'C': 3, 'Ç': 4, 'D': 5, 'E': 6, 'F': 7, 'G': 8, 'Ğ': 9, 'H': 10,
        'I': 11, 'İ': 12, 'J': 13, 'K': 14, 'L': 15, 'M': 16, 'N': 17, 'O': 18, 'Ö': 19,
        'P': 20, 'R': 21, 'S': 22, 'Ş': 23, 'T': 24, 'U': 25, 'Ü': 26, 'V': 27, 'Y': 28, 'Z': 29
    }
    
    metin_kucuk = metin.lower()
    anahtar = []
    
    for harf in metin_kucuk:
        if harf in turkce_harf_agirliklari:
            anahtar.append(f"{turkce_harf_agirliklari[harf]:02d}")
        else:
            anahtar.append("99")
    
    return "".join(anahtar)

class SinavPDF(FPDF):
    def __init__(self, uni, fakulte, bolum, ders, sinav_turu, tarih, saat, hoca, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.uni_str = uni
        self.fak_str = fakulte
        self.bol_str = bolum
        self.der_str = ders
        self.sinav_turu = sinav_turu
        self.tar_str = tarih
        self.saa_str = saat
        self.hoc_str = hoca
        
        # UTF-8 desteğini etkinleştir
        self.set_auto_page_break(auto=True, margin=15)
        
        font_secenekleri = [
            ("Arial", "C:\\Windows\\Fonts\\arial.ttf", "C:\\Windows\\Fonts\\arialbd.ttf"),
            ("Calibri", "C:\\Windows\\Fonts\\calibri.ttf", "C:\\Windows\\Fonts\\calibrib.ttf"),
            ("Times New Roman", "C:\\Windows\\Fonts\\times.ttf", "C:\\Windows\\Fonts\\timesbd.ttf"),
            # Linux/Streamlit Cloud için alternatif font yolları
            ("DejaVu", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
            ("LiberationSans", "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf")
        ]
        
        self.fnt = 'Helvetica'
        self.font_added = False
        
        for font_adi, font_yolu, font_yolu_bold in font_secenekleri:
            if os.path.exists(font_yolu) and os.path.exists(font_yolu_bold):
                try:
                    self.add_font(font_adi, '', font_yolu, uni=True)
                    self.add_font(font_adi, 'B', font_yolu_bold, uni=True)
                    self.fnt = font_adi
                    self.font_added = True
                    break
                except Exception as e:
                    continue
        
        if not self.font_added:
            # Font eklenemediyse, Türkçe karakterler için uygun bir font kullan
            try:
                # Arial Unicode MS gibi geniş karakter seti olan bir font deneyelim
                self.add_font('ArialUnicode', '', 'arialuni.ttf', uni=True)
                self.add_font('ArialUnicode', 'B', 'arialunib.ttf', uni=True)
                self.fnt = 'ArialUnicode'
                self.font_added = True
            except:
                # Hiçbir font eklenemezse Helvetica kullan ama Türkçe karakterleri değiştir
                self.fnt = 'Helvetica'
                # Türkçe karakter mapping
                self.turkce_replace = {
                    'ç': 'c', 'ğ': 'g', 'ı': 'i', 'ö': 'o', 'ş': 's', 'ü': 'u',
                    'Ç': 'C', 'Ğ': 'G', 'İ': 'I', 'Ö': 'O', 'Ş': 'S', 'Ü': 'U'
                }

    def _clean_text(self, text):
        """Türkçe karakterleri temizle (eğer font desteklemiyorsa)"""
        if not hasattr(self, 'font_added') or not self.font_added:
            if hasattr(self, 'turkce_replace'):
                for turkce, latin in self.turkce_replace.items():
                    text = text.replace(turkce, latin)
        return text

    def yoklama_header(self, sinif):
        # Başlıkları temizle
        uni_clean = self._clean_text(self.uni_str)
        fak_clean = self._clean_text(self.fak_str)
        bol_clean = self._clean_text(self.bol_str)
        der_clean = self._clean_text(self.der_str)
        sinif_clean = self._clean_text(sinif)
        
        self.set_font(self.fnt, 'B', 10)
        self.cell(0, 5, f"{uni_clean} {fak_clean}", ln=True, align='C')
        self.cell(0, 5, f"{bol_clean} {self._clean_text(self.sinav_turu)} TUTANAĞI", ln=True, align='C')
        self.ln(5)
        
        self.set_font(self.fnt, 'B', 9)
        self.cell(25, 8, " Dersin Adı", 1)
        self.set_font(self.fnt, '', 9)
        self.cell(168, 8, f" {der_clean}", 1, ln=True)
        
        self.set_font(self.fnt, 'B', 9)
        self.cell(25, 8, " Sınıf No", 1)
        self.set_font(self.fnt, '', 9)
        self.cell(40, 8, f" {sinif_clean}", 1)
        
        self.set_font(self.fnt, 'B', 9)
        self.cell(20, 8, " Tarih", 1)
        self.set_font(self.fnt, '', 9)
        self.cell(45, 8, f" {self.tar_str}", 1)
        
        self.set_font(self.fnt, 'B', 9)
        self.cell(21, 8, " Saat", 1)
        self.set_font(self.fnt, '', 9)
        self.cell(42, 8, f" {self.saa_str}", 1, ln=True)
        self.ln(3)

    def kapi_listesi_header(self, sinif):
        # Başlıkları temizle
        uni_clean = self._clean_text(self.uni_str)
        fak_clean = self._clean_text(self.fak_str)
        bol_clean = self._clean_text(self.bol_str)
        der_clean = self._clean_text(self.der_str)
        sinif_clean = self._clean_text(sinif)
        
        self.set_font(self.fnt, 'B', 14)
        self.cell(0, 8, uni_clean, ln=True, align='C')
        self.ln(2)
        
        self.set_font(self.fnt, 'B', 12)
        self.cell(0, 7, fak_clean, ln=True, align='C')
        self.ln(2)
        
        self.set_font(self.fnt, 'B', 11)
        self.cell(0, 6, f"{bol_clean} - {der_clean} {self._clean_text(self.sinav_turu)}", ln=True, align='C')
        self.ln(3)
        
        self.set_font(self.fnt, 'B', 13)
        self.cell(0, 8, f"Sınıf Listesi - {sinif_clean}", ln=True, align='C')
        self.ln(8)
    
    def yoklama_tablo(self, room_list, sinif_adi):
        """Dinamik yoklama tablosu - öğrenci sayısına göre otomatik ayarlanır"""
        sinif_adi_clean = self._clean_text(sinif_adi)
        
        # Tablo başlıkları
        self.set_font(self.fnt, 'B', 8)
        for _ in range(2):
            self.cell(8, 7, "S.N", 1, 0, 'C')
            self.cell(20, 7, "No", 1, 0, 'C')
            self.cell(42, 7, "Adı Soyadı", 1, 0, 'C')
            self.cell(25, 7, "İmza", 1, 0, 'C')
            if _ == 0: self.cell(2, 7, "", 0, 0)
        self.ln(7)
        
        # Öğrenci sayısını al
        ogrenci_sayisi = len(room_list)
        
        # Kaç sayfa gerektiğini hesapla (her sayfa 50 kişi)
        sayfa_sayisi = math.ceil(ogrenci_sayisi / 50)
        
        for sayfa_no in range(sayfa_sayisi):
            if sayfa_no > 0:
                self.add_page()
                self.yoklama_header(sinif_adi_clean)
                # Tablo başlıklarını tekrar yaz
                self.set_font(self.fnt, 'B', 8)
                for _ in range(2):
                    self.cell(8, 7, "S.N", 1, 0, 'C')
                    self.cell(20, 7, "No", 1, 0, 'C')
                    self.cell(42, 7, "Adı Soyadı", 1, 0, 'C')
                    self.cell(25, 7, "İmza", 1, 0, 'C')
                    if _ == 0: self.cell(2, 7, "", 0, 0)
                self.ln(7)
            
            # Bu sayfadaki öğrenci aralığı
            baslangic = sayfa_no * 50
            bitis = min((sayfa_no + 1) * 50, ogrenci_sayisi)
            
            # İlk 25 öğrenci için
            self.set_font(self.fnt, '', 7.5)
            for i in range(25):
                sira_no = baslangic + i
                if sira_no < bitis:
                    s = room_list.iloc[sira_no]
                    ad_soyad = f"{s.iloc[1]} {s.iloc[2]}"
                    ad_soyad_clean = self._clean_text(ad_soyad)
                    self.cell(8, 6.5, str(sira_no + 1), 1, 0, 'C')
                    self.cell(20, 6.5, str(s.iloc[0]), 1, 0, 'C')
                    self.cell(42, 6.5, f" {ad_soyad_clean}", 1, 0, 'L')
                    self.cell(25, 6.5, "", 1, 0)
                else:
                    for w in [8, 20, 42, 25]: self.cell(w, 6.5, "", 1, 0)
                self.cell(2, 6.5, "", 0, 0)
                
                # Sağ taraftaki 25 öğrenci (26-50)
                sira_no_sag = baslangic + i + 25
                if sira_no_sag < bitis:
                    s = room_list.iloc[sira_no_sag]
                    ad_soyad = f"{s.iloc[1]} {s.iloc[2]}"
                    ad_soyad_clean = self._clean_text(ad_soyad)
                    self.cell(8, 6.5, str(sira_no_sag + 1), 1, 0, 'C')
                    self.cell(20, 6.5, str(s.iloc[0]), 1, 0, 'C')
                    self.cell(42, 6.5, f" {ad_soyad_clean}", 1, 0, 'L')
                    self.cell(25, 6.5, "", 1, 1)
                else:
                    for w in [8, 20, 42]: self.cell(w, 6.5, "", 1, 0)
                    self.cell(25, 6.5, "", 1, 1)
            
            # **DEĞİŞİKLİK BAŞLANGICI: Her sayfaya alt bilgileri ekle**
            self.ln(4)
            self.set_font(self.fnt, '', 9)
            self.cell(0, 5, "Bu sınıfta ................. öğrenci sınava girmiş ve sınav kağıtları teslim edilmiştir.", ln=True)
            self.ln(2)
            
            y_pos = self.get_y()
            box_w = 62.4

            for j in range(3):
                x_coord = 10 + (j * (box_w + 1.9))
                self.rect(x_coord, y_pos, box_w, 25)
                self.set_xy(x_coord, y_pos + 1)
                titles = ["Gözetmen 1", "Gözetmen 2", "Öğretim Üyesi"]
                self.set_font(self.fnt, 'B', 9)
                self.cell(box_w, 5, titles[j], 0, 1, 'C')
                self.set_font(self.fnt, '', 8)
                if j == 2:
                    hoca_clean = self._clean_text(self.hoc_str)
                    self.set_x(x_coord); self.cell(box_w, 5, f" {hoca_clean}", 0, 1, 'C')
                else:
                    self.set_x(x_coord); self.cell(box_w, 5, " Adı Soyadı:", 0, 1, 'L')
                self.set_x(x_coord); self.cell(box_w, 5, " İmza:", 0, 1, 'L')
            # **DEĞİŞİKLİK SONU**
    
    def kapi_listesi_tablo(self, room_list, sinif_adi):
        """Dinamik kapı listesi tablosu - öğrenci sayısına göre otomatik ayarlanır"""
        sinif_adi_clean = self._clean_text(sinif_adi)
        
        # Tablo başlıkları
        self.set_font(self.fnt, 'B', 8)
        for _ in range(2):
            self.cell(8, 7, "S.N", 1, 0, 'C')
            self.cell(20, 7, "No", 1, 0, 'C')
            self.cell(70, 7, "Adı Soyadı", 1, 0, 'C')
            if _ == 0: self.cell(2, 7, "", 0, 0)
        self.ln(7)
        
        # Öğrenci sayısını al
        ogrenci_sayisi = len(room_list)
        
        # Kaç sayfa gerektiğini hesapla (her sayfa 50 kişi)
        sayfa_sayisi = math.ceil(ogrenci_sayisi / 50)
        
        for sayfa_no in range(sayfa_sayisi):
            if sayfa_no > 0:
                self.add_page()
                self.kapi_listesi_header(sinif_adi_clean)
                # Tablo başlıklarını tekrar yaz
                self.set_font(self.fnt, 'B', 8)
                for _ in range(2):
                    self.cell(8, 7, "S.N", 1, 0, 'C')
                    self.cell(20, 7, "No", 1, 0, 'C')
                    self.cell(70, 7, "Adı Soyadı", 1, 0, 'C')
                    if _ == 0: self.cell(2, 7, "", 0, 0)
                self.ln(7)
            
            # Bu sayfadaki öğrenci aralığı
            baslangic = sayfa_no * 50
            bitis = min((sayfa_no + 1) * 50, ogrenci_sayisi)
            
            # İlk 25 öğrenci için
            self.set_font(self.fnt, '', 7.5)
            for i in range(25):
                sira_no = baslangic + i
                if sira_no < bitis:
                    s = room_list.iloc[sira_no]
                    ad_soyad = f"{s.iloc[1]} {s.iloc[2]}"
                    ad_soyad_clean = self._clean_text(ad_soyad)
                    self.cell(8, 6.5, str(sira_no + 1), 1, 0, 'C')
                    self.cell(20, 6.5, str(s.iloc[0]), 1, 0, 'C')
                    self.cell(70, 6.5, f" {ad_soyad_clean}", 1, 0, 'L')
                else:
                    for w in [8, 20, 70]: self.cell(w, 6.5, "", 1, 0)
                self.cell(2, 6.5, "", 0, 0)
                
                # Sağ taraftaki 25 öğrenci (26-50)
                sira_no_sag = baslangic + i + 25
                if sira_no_sag < bitis:
                    s = room_list.iloc[sira_no_sag]
                    ad_soyad = f"{s.iloc[1]} {s.iloc[2]}"
                    ad_soyad_clean = self._clean_text(ad_soyad)
                    self.cell(8, 6.5, str(sira_no_sag + 1), 1, 0, 'C')
                    self.cell(20, 6.5, str(s.iloc[0]), 1, 0, 'C')
                    self.cell(70, 6.5, f" {ad_soyad_clean}", 1, 1, 'L')
                else:
                    for w in [8, 20, 70]: self.cell(w, 6.5, "", 1, 0)
                    self.ln(6.5)

st.set_page_config(page_title="Sınav Yoklama ve Duyuru Sistemi", layout="wide")
st.title("🎓 Sınav Yoklama ve Duyuru Sistemi")

with st.expander("📋 Sistem Kullanım Talimatları", expanded=False):
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        **İşlem Sırası:**
        1. Sağdaki butondan şablon Excel dosyasını indiriniz
        2. Sol taraftan sınava ait tüm bilgileri (üniversite, fakülte, bölüm, ders, sınav türü, tarih, saat, öğretim üyesi) giriniz
           **Not:** Bu kısımlar tarayıcı önbelleğinden otomatik olarak doldurulsa bile her alana en az bir kez mouse ile tıklayınız
        3. Sol taraftan sınav yapılacak sınıfları ve kapasitelerini tek tek ekleyiniz
        4. Öğrenci otomasyon sisteminden öğrenci listesini kopyalayınız
        5. Şablondaki ilgili alanlara (No, Ad, Soyad) yapıştırınız
        6. Dosyayı **"sinav_sablon_ogr_list.xlsx"** olarak kaydediniz (isim kesinlikle değiştirilmemeli)
        7. Aşağıdaki BROWSE alanından dosyayı yükleyiniz
        8. **'Tüm Belgeleri Oluştur'** butonuna basarak PDF belgelerinizi oluşturunuz
        
        **Dikkat:**
        - Şablon dosyasının ismini kesinlikle değiştirmeyiniz, aksi takdirde sistem çalışmaz
        - Toplam sınıf kapasitesi Excel'deki öğrenci sayısı ile tam olarak eşleşmeli
        - Örneğin, 144 öğrenci için 50-50-44 veya 48-48-48 şeklinde dağıtım yapılabilir
        - Toplam kapasite ne eksik ne fazla olmalıdır
       """)
    
    with col2:
        template_data = pd.DataFrame({
            "No": [""],
            "Ad": [""],
            "Soyad": [""]
        })

        template_buffer = io.BytesIO()
        with pd.ExcelWriter(template_buffer, engine='openpyxl') as writer:
            template_data.to_excel(writer, index=False, sheet_name='Öğrenci Listesi')
        template_buffer.seek(0)

        st.download_button(
            label="📥 Şablonu İndir",
            data=template_buffer,
            file_name="sinav_sablon_ogr_list.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

st.divider()

if 'rooms' not in st.session_state:
    st.session_state.rooms = []

with st.sidebar:
    st.header("📋 Sınav Bilgileri")
    
    uni_inp = st.text_input("Üniversite", placeholder="Üniversite adını giriniz")
    fak_inp = st.text_input("Fakülte", placeholder="Fakülte adını giriniz")
    bol_inp = st.text_input("Bölüm", placeholder="Bölüm adını giriniz")
    der_inp = st.text_input("Dersin Adı", placeholder="Ders adını giriniz")
    
    sinav_turu_inp = st.selectbox(
        "Sınav Türü",
        ["Vize Sınavı", "Final Sınavı", "Bütünleme Sınavı", "Mazeret Sınavı", "Diğer"]
    )
    
    hoc_inp = st.text_input("Öğretim Üyesi", placeholder="Öğretim üyesi adını giriniz")
    tar_inp = st.text_input("Sınav Tarihi", placeholder="GG.AA.YYYY")
    saa_inp = st.text_input("Sınav Saati", placeholder="SS:DD")
    
    st.divider()
    st.subheader("🏫 Sınıf Tanımlama")
    
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        rn = st.text_input("Sınıf Adı", key="sinif_adi", placeholder="A1, B2, vs.")
    with c2:
        rc = st.number_input("Kapasite", 1, 300, 50, key="kapasite")
    with c3:
        st.write("")
        st.write("")
        if st.button("Ekle", type="primary", use_container_width=True):
            if rn:
                st.session_state.rooms.append({"Ad": rn, "Kap": int(rc)})
                st.rerun()
            else:
                st.warning("Lütfen sınıf adı giriniz")
    
    if st.session_state.rooms:
        st.divider()
        st.subheader("📋 Tanımlı Sınıflar")
        
        total_capacity = 0
        rooms_display = st.container()
        
        with rooms_display:
            cols = st.columns(3)
            for idx, r in enumerate(st.session_state.rooms):
                with cols[idx % 3]:
                    st.info(f"**{r['Ad']}**\n({r['Kap']} kişi)")
                total_capacity += r['Kap']
        
        st.info(f"**Toplam Kapasite:** {total_capacity} öğrenci")
        
        if st.button("🗑️ Tümünü Temizle", use_container_width=True, type="secondary"):
            st.session_state.rooms = []
            st.rerun()

st.subheader("📤 Excel Dosyasını Yükleme")
uploaded_file = st.file_uploader("Öğrenci listesi Excel dosyasını yükleyin (sinav_sablon_ogr_list.xlsx)", type=["xlsx"])

if uploaded_file:
    try:
        if uploaded_file.name != "sinav_sablon_ogr_list.xlsx":
            st.warning("Lütfen indirdiğiniz şablon dosyasını değiştirmeden kullanın. Dosya adı 'sinav_sablon_ogr_list.xlsx' olmalıdır.")
        
        df = pd.read_excel(uploaded_file)
        
        if len(df.columns) >= 3:
            st.success(f"✅ {len(df)} öğrenci başarıyla yüklendi!")
            
            if st.session_state.rooms:
                total_capacity = sum(r['Kap'] for r in st.session_state.rooms)
                if total_capacity != len(df):
                    st.error(f"⚠️ Uyarı: Toplam sınıf kapasitesi ({total_capacity}) öğrenci sayısı ({len(df)}) ile uyuşmuyor!")
                    st.info(f"Lütfen sınıf kapasitelerini toplamı {len(df)} olacak şekilde düzenleyin.")
                else:
                    st.success(f"✓ Sınıf kapasitesi ({total_capacity}) öğrenci sayısı ile uyuşuyor.")
        else:
            st.error("Excel dosyasında en az 3 sütun (No, Ad, Soyad) olmalıdır.")
    except Exception as e:
        st.error(f"Dosya okunurken hata oluştu: {str(e)}")

if uploaded_file and st.session_state.rooms:
    df = pd.read_excel(uploaded_file)
    total_capacity = sum(r['Kap'] for r in st.session_state.rooms)
    
    required_fields = [uni_inp, fak_inp, bol_inp, der_inp, sinav_turu_inp, hoc_inp, tar_inp, saa_inp]
    field_names = ["Üniversite", "Fakülte", "Bölüm", "Ders", "Sınav Türü", "Öğretim Üyesi", "Tarih", "Saat"]
    
    missing_fields = []
    for field, name in zip(required_fields, field_names):
        if not field or field.strip() == "":
            missing_fields.append(name)
    
    if missing_fields:
        st.error(f"Lütfen aşağıdaki alanları doldurun: {', '.join(missing_fields)}")
    elif total_capacity == len(df):
        if st.button("🚀 Tüm Belgeleri Oluştur", type="primary", use_container_width=True):
            with st.spinner("Belgeler oluşturuluyor..."):
                shuffled = df.sample(frac=1).reset_index(drop=True)
                zip_buffer = io.BytesIO()
                
                with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                    ptr = 0
                    all_assigned_students = []

                    for room in st.session_state.rooms:
                        end_ptr = ptr + room['Kap']
                        room_list = shuffled.iloc[ptr:end_ptr].sort_values(by=df.columns[0]).reset_index(drop=True)
                        ptr = end_ptr
                        
                        temp_df = room_list.copy()
                        temp_df['Sınıf'] = room['Ad']
                        all_assigned_students.append(temp_df)

                        # YOKLAMA PDF (DİNAMİK)
                        pdf = SinavPDF(uni_inp, fak_inp, bol_inp, der_inp, sinav_turu_inp, tar_inp, saa_inp, hoc_inp)
                        pdf.add_page()
                        pdf.yoklama_header(room['Ad'])
                        pdf.yoklama_tablo(room_list, room['Ad'])

                        pdf_output = pdf.output(dest='S').encode('latin-1', 'replace')
                        zip_file.writestr(f"Yoklama_{room['Ad']}.pdf", pdf_output)

                        # KAPI LİSTESİ PDF (DİNAMİK)
                        pdf_kapi = SinavPDF(uni_inp, fak_inp, bol_inp, der_inp, sinav_turu_inp, tar_inp, saa_inp, hoc_inp)
                        pdf_kapi.add_page()
                        pdf_kapi.kapi_listesi_header(room['Ad'])
                        pdf_kapi.kapi_listesi_tablo(room_list, room['Ad'])

                        kapi_output = pdf_kapi.output(dest='S').encode('latin-1', 'replace')
                        zip_file.writestr(f"Kapi_Listesi_{room['Ad']}.pdf", kapi_output)

                    # PANO LİSTESİ (DEĞİŞMEDİ)
                    pano_df = pd.concat(all_assigned_students).reset_index(drop=True)
                    pano_df['Siralama_Anahtari'] = pano_df.iloc[:, 2].apply(turkce_sirala_anahtar)
                    pano_df = pano_df.sort_values(by='Siralama_Anahtari').reset_index(drop=True)
                    pano_df.insert(0, 'Sıra', range(1, len(pano_df) + 1))
                    
                    pdf_p = SinavPDF(uni_inp, fak_inp, bol_inp, der_inp, sinav_turu_inp, tar_inp, saa_inp, hoc_inp)
                    pdf_p.add_page()
                    pdf_p.set_font(pdf_p.fnt, 'B', 12)
                    pdf_p.cell(0, 10, f"{self._clean_text(der_inp)} {self._clean_text(sinav_turu_inp)} YERLEŞİM PLANI", ln=True, align='C')
                    pdf_p.ln(5)
                    
                    pdf_p.set_font(pdf_p.fnt, 'B', 9)
                    pdf_p.cell(15, 8, "Sıra", 1, 0, 'C')
                    pdf_p.cell(25, 8, "No", 1, 0, 'C')
                    pdf_p.cell(50, 8, "Adı", 1)
                    pdf_p.cell(50, 8, "Soyadı", 1)
                    pdf_p.cell(25, 8, "SINIF", 1, 1, 'C')
                    
                    pdf_p.set_font(pdf_p.fnt, '', 7.5)
                    for r in pano_df.itertuples(index=False):
                        ad_clean = pdf_p._clean_text(str(r[2]))
                        soyad_clean = pdf_p._clean_text(str(r[3]))
                        sinif_clean = pdf_p._clean_text(str(r[4]))
                        pdf_p.cell(15, 7, str(r[0]), 1, 0, 'C')
                        pdf_p.cell(25, 7, str(r[1]), 1, 0, 'C')
                        pdf_p.cell(50, 7, f" {ad_clean}", 1)
                        pdf_p.cell(50, 7, f" {soyad_clean}", 1)
                        pdf_p.cell(25, 7, f" {sinif_clean}", 1, 1, 'C')
                    
                    p_output = pdf_p.output(dest='S').encode('latin-1', 'replace')
                    zip_file.writestr("Pano_Listesi.pdf", p_output)

            st.success("✅ Tüm belgeler başarıyla oluşturuldu!")
            
            st.download_button(
                label="📥 Tüm Belgeleri İndir (ZIP)",
                data=zip_buffer.getvalue(),
                file_name="sinav_belgeleri.zip",
                mime="application/zip",
                use_container_width=True
            )
            
            st.info(f"""
            **Oluşturulan Dosyalar:**
            - Yoklama Listeleri: {len(st.session_state.rooms)} adet (her biri gerekirse çok sayfalı)
            - Kapı Listeleri: {len(st.session_state.rooms)} adet (her biri gerekirse çok sayfalı)  
            - Pano Listesi: 1 adet (Türkçe alfabetik sıralı)
            
            **Toplam:** {2*len(st.session_state.rooms) + 1} PDF dosyası
            **Not:** Büyük sınıflar için otomatik çok sayfalı PDF'ler oluşturuldu.
            """)
    else:
        st.warning("Lütfen önce sınıf kapasitelerini öğrenci sayısı ile eşleştirin.")

st.divider()
st.caption("📧 [Designed by Refik YASLIKAYA](mailto:refik@kku.edu.tr) | Sınav Yoklama ve Duyuru Sistemi v1.0")