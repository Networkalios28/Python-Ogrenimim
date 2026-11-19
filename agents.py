"""
agents.py
3. Katman: Semptom Ayrıştırıcı ve Klinik Karar Motoru
Trakya Üniversitesi Bilişim Sistemleri ve Teknolojileri - Doç. Dr. Murat Topaloğlu
"""

import json
import re
from typing import Dict, Any, Optional


class SemptomAyrıştırmaAjanı:
    SYSTEM_PROMPT = """Sen acil servis triyajında uzmanlaşmış bir Klinik Karar Destek Sistemisin.
Görevin hastanın yazdığı şikayeti klinik olarak analiz etmek ve KESİNLİKLE aşağıdaki JSON formatında çıktı vermektir:

{
    "tibbi_semptomlar": ["tespit edilen semptomlar"],
    "etkilenen_bolge": "vücut bölgesi / sistem",
    "oneri_aciliyet": "KIRMIZI | SARI | YESIL",
    "ilgili_brans": "İlgili Tıbbi Branş",
    "klinik_gerekce": "Kısa klinik değerlendirme açıklaması"
}

Klinik Kurallar:
- Bıçaklanma, kurşunlanma, şişlenme, delici/kesici alet yaralanması, masif kanama, bilincin kapalı olması, göğüste ezici baskı ve solunum durması KESİNLİKLE KIRMIZI ALANDIR.
- Göz travmaları, göze yabancı cisim batması/gelmesi, gözde kanlanma/kızarma, kimyasal temas ve ani görme kaybı KESİNLİKLE YEŞİL ALAN OLAMAZ; en az SARI ALANDIR (İlgili Branş: Göz Hastalıkları / Acil Tıp).
- Akut idrar yapamama (retansiyon/glob), şiddetli karın ağrısı, kontrol altına alınabilen aktif kanamalar, kırık şüphesi en az SARI ALANDIR.
- Yüzeysel çizikler, sürtünmeler, ufak sıyrıklar (paslı demir/sıra çizmesi vb.) YEŞİL ALANDIR (Tetanos/Pansuman).
- Sadece saf JSON üret. Başına veya sonuna hiçbir markdown (```json vb.) ekleme.
"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key.strip() if api_key else None
        self.client = None
        self.son_hata = None
        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                self.son_hata = f"Client Başlatılamadı: {e}"

    def analiz_et(self, sikayet_metni: str) -> Dict[str, Any]:
        if self.client:
            try:
                prompt = f"{self.SYSTEM_PROMPT}\n\nHasta Şikayeti: \"{sikayet_metni}\""
                response = self.client.models.generate_content(
                    model='gemini-3.8-flash',
                    contents=prompt
                )
                temiz = re.sub(r"```json|```", "", response.text).strip()
                return json.loads(temiz)
            except Exception as e:
                self.son_hata = f"API Hatası: {e}"
                return self._gelismis_yerel_analiz(sikayet_metni)
        
        return self._gelismis_yerel_analiz(sikayet_metni)

    def _gelismis_yerel_analiz(self, metin: str) -> Dict[str, Any]:
        m = metin.lower()

        # 1. BIÇAKLANMA / SALDIRI / DELİCİ TRAVMA (KESİNLİKLE KIRMIZI)
        kritik_saldiri = ["bıçaklan", "bıçaklandı", "kurşun", "vuruldu", "şişlendi", "kesildi", "boğazlandı", "ateşli silah", "saplandı", "demir girdi"]
        if any(k in m for k in kritik_saldiri):
            return {
                "tibbi_semptomlar": ["Penetran Bıçak/Silah Yaralanması", "İç organ perforasyonu ve masif kanama riski"],
                "etkilenen_bolge": "Torakoabdominal / Yumuşak Doku",
                "oneri_aciliyet": "KIRMIZI",
                "ilgili_brans": "Acil Cerrahi / Travmatoloji",
                "klinik_gerekce": "Delici/kesici alet veya ateşli silah yaralanmaları hayatı tehdit eden cerrahi tablolardır; derhal resüsitasyon odasına alınmalıdır."
            }

        # 2. GÖZ TRAVMALARI VE YABANCI CİSİM (KESİNLİKLE EN AZ SARI)
        if "göz" in m and any(g in m for g in ["plastik", "cisim", "demir", "toz", "darbe", "kırmızı", "kan", "görmüyorum", "bat"]):
            return {
                "tibbi_semptomlar": ["Oküler travma şüphesi", "Kornea yabancı cisim / konjonktival hasar riski"],
                "etkilenen_bolge": "Görme Sistemi (Göz)",
                "oneri_aciliyet": "SARI",
                "ilgili_brans": "Göz Hastalıkları / Acil Tıp",
                "klinik_gerekce": "Göze yabancı cisim teması kornea perforasyonu veya mekanik travma riski taşır; ivedilikle biyomikroskopi muayenesi gerektirir."
            }

        # 3. YÜZEYSEL ÇİZİK / PASLI DEMİR (YEŞİL ALAN)
        cizik_kelimeleri = ["çizdi", "sıyrık", "hafif kesti", "sürtündü", "yüzeysel"]
        if any(c in m for c in cizik_kelimeleri) and not any(k in m for k in kritik_saldiri):
            return {
                "tibbi_semptomlar": ["Yüzeysel doku sıyrığı", "Tetanos profilaksisi gereksinimi"],
                "etkilenen_bolge": "Deri ve Yumuşak Doku",
                "oneri_aciliyet": "YESIL",
                "ilgili_brans": "Acil Yeşil Alan / Aşı Birimi",
                "klinik_gerekce": "Yüzeysel yaralanma ve çizik; hayati risk saptanmadı. Yara yeri pansumanı ve tetanos aşısı kontrolü gerektirir."
            }

        # 4. KALP / GÖĞÜS AĞRISI (KIRMIZI ALAN)
        if any(k in m for k in ["göğüs", "kalp", "sol kol", "baskı", "fil oturmuş", "çarpıntı"]):
            return {
                "tibbi_semptomlar": ["Akut koroner sendrom şüphesi", "Göğüs ağrısı"],
                "etkilenen_bolge": "Kardiyovasküler Sistem",
                "oneri_aciliyet": "KIRMIZI",
                "ilgili_brans": "Kardiyoloji / Acil Tıp",
                "klinik_gerekce": "Göğüste baskı ve yayılım gösteren ağrılar miyokard enfarktüsü riski taşır; acil EKG gereklidir."
            }

        # 5. İDRAR RETANSİYONU (SARI ALAN)
        if any(i in m for i in ["idrar", "çiş", "damla"]) and any(y in m for y in ["çıkaramama", "yapamıyorum", "gelmiyor", "çıkmıyor"]):
            return {
                "tibbi_semptomlar": ["Akut üriner retansiyon (Glob vezikale)"],
                "etkilenen_bolge": "Genitoüriner Sistem (Mesane)",
                "oneri_aciliyet": "SARI",
                "ilgili_brans": "Üroloji / Acil Tıp",
                "klinik_gerekce": "Akut üriner retansiyon mesane hasarı ve böbrek yetmezliği riski nedeniyle acil sonda uygulanmasını gerektirir."
            }

        # 6. KANAMA KONTROLLERİ (SARI ALAN)
        if any(k in m for k in ["kan", "kanama", "kanıyor"]):
            return {
                "tibbi_semptomlar": ["Aktif kanama odağı"],
                "etkilenen_bolge": "Genel / Semptoma Göre",
                "oneri_aciliyet": "SARI",
                "ilgili_brans": "Acil Tıp / İlgili Cerrahi",
                "klinik_gerekce": "Aktif kanamalar hekim değerlendirmesi ve kanama kontrolü gerektirir."
            }

        # 7. GENEL AYAKTAN POLİKLİNİK (YEŞİL ALAN)
        return {
            "tibbi_semptomlar": ["Stabil klinik tablo"],
            "etkilenen_bolge": "Genel",
            "oneri_aciliyet": "YESIL",
            "ilgili_brans": "Genel Dahiliye / Aile Hekimliği",
            "klinik_gerekce": "Acil kırmızı veya sarı bayrak saptanmadı; ayaktan muayene uygundur."
        }