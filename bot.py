from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
import os
import sys
from typing import Optional

app = FastAPI(title="Mernis + Depremzede API", 
              description="Mernis ve Depremzede sorgulama")

# ============ VERİ YÜKLEME ============

def load_mernis():
    """Mernis verilerini otomatik algıla - TC|AD|SOYAD|İL veya TC|ADRES|SOYAD|İL"""
    data = {}
    dosya_adi = "mernisvip.txt"
    
    print(f"📂 {dosya_adi} okunuyor...")
    
    if not os.path.exists(dosya_adi):
        print(f"❌ {dosya_adi} dosyası BULUNAMADI!")
        return data
    
    try:
        with open(dosya_adi, "r", encoding="utf-8") as f:
            satir_sayisi = 0
            for line in f:
                line = line.strip()
                if not line:
                    continue
                if "|" not in line:
                    continue
                    
                parts = line.split("|")
                if len(parts) < 4:
                    continue
                    
                tc = parts[0].strip()
                if not tc:
                    continue
                
                # Formatı otomatik algıla
                # Eğer 2. alan uzunsa (adres) veya içinde / varsa adres olarak algıla
                alan2 = parts[1].strip() if len(parts) > 1 else ""
                alan3 = parts[2].strip() if len(parts) > 2 else ""
                alan4 = parts[3].strip() if len(parts) > 3 else ""
                
                # Adres formatı mı? (içinde / veya Mah. varsa)
                if "/" in alan2 or "Mah" in alan2 or "Cad" in alan2 or "Sok" in alan2:
                    data[tc] = {
                        "adres": alan2,
                        "soyad": alan3,
                        "il": alan4
                    }
                else:
                    # Değilse AD|SOYAD|İL formatı
                    data[tc] = {
                        "ad": alan2,
                        "soyad": alan3,
                        "il": alan4
                    }
                satir_sayisi += 1
            
            print(f"✅ Mernis: {satir_sayisi} satır okundu, {len(data)} kayıt yüklendi")
            
    except Exception as e:
        print(f"❌ {dosya_adi} okunurken hata: {e}")
    
    return data

def load_depremzede():
    """Depremzede verilerini otomatik algıla"""
    data = []
    dosya_adi = "depremzede.txt"
    
    print(f"📂 {dosya_adi} okunuyor...")
    
    if not os.path.exists(dosya_adi):
        print(f"❌ {dosya_adi} dosyası BULUNAMADI!")
        return data
    
    try:
        with open(dosya_adi, "r", encoding="utf-8") as f:
            satir_sayisi = 0
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                # Virgül ile ayır (CSV)
                parts = line.split(",")
                if len(parts) >= 5:
                    # Tırnakları temizle
                    ad_soyad = parts[1].strip().strip('"') if len(parts) > 1 else ""
                    poliklinik = parts[2].strip().strip('"') if len(parts) > 2 else ""
                    hastane = parts[3].strip().strip('"') if len(parts) > 3 else ""
                    gelis_sekli = parts[4].strip().strip('"') if len(parts) > 4 else ""
                    il = parts[5].strip().strip('"') if len(parts) > 5 else ""
                    
                    data.append({
                        "ad_soyad": ad_soyad,
                        "poliklinik": poliklinik,
                        "hastane": hastane,
                        "gelis_sekli": gelis_sekli,
                        "il": il
                    })
                    satir_sayisi += 1
                
                # Pipe ile ayır (alternatif format)
                elif "|" in line:
                    parts = line.split("|")
                    if len(parts) >= 5:
                        data.append({
                            "ad_soyad": parts[0].strip(),
                            "poliklinik": parts[1].strip() if len(parts) > 1 else "",
                            "hastane": parts[2].strip() if len(parts) > 2 else "",
                            "gelis_sekli": parts[3].strip() if len(parts) > 3 else "",
                            "il": parts[4].strip() if len(parts) > 4 else ""
                        })
                        satir_sayisi += 1
                
                # Boşluk ile ayır (alternatif format)
                elif " " in line:
                    parts = line.split(maxsplit=4)
                    if len(parts) >= 5:
                        data.append({
                            "ad_soyad": parts[0].strip(),
                            "poliklinik": parts[1].strip() if len(parts) > 1 else "",
                            "hastane": parts[2].strip() if len(parts) > 2 else "",
                            "gelis_sekli": parts[3].strip() if len(parts) > 3 else "",
                            "il": parts[4].strip() if len(parts) > 4 else ""
                        })
                        satir_sayisi += 1
            
            print(f"✅ Depremzede: {satir_sayisi} satır okundu, {len(data)} kayıt yüklendi")
            
    except Exception as e:
        print(f"❌ {dosya_adi} okunurken hata: {e}")
    
    return data

# ============ VERİLERİ YÜKLE ============

print("=" * 60)
print("📊 VERİ YÜKLEME BAŞLADI")
print("=" * 60)

# Mevcut dosyaları listele
print("📁 Mevcut dosyalar:")
for f in os.listdir("."):
    if f.endswith(".txt"):
        boyut = os.path.getsize(f) if os.path.exists(f) else 0
        print(f"   {f} ({boyut} byte)")

print("=" * 60)

mernis_data = load_mernis()
depremzede_data = load_depremzede()

print("=" * 60)
print(f"📊 YÜKLEME SONUÇLARI:")
print(f"   Mernis: {len(mernis_data)} kayıt")
print(f"   Depremzede: {len(depremzede_data)} kayıt")
print("=" * 60)

# ============ API ENDPOINT'LERİ ============

@app.get("/")
def root():
    return {
        "message": "Mernis + Depremzede API",
        "mernis_kayit": len(mernis_data),
        "depremzede_kayit": len(depremzede_data)
    }

@app.get("/mernis")
def mernis_sorgula(
    tc: Optional[str] = None,
    ad: Optional[str] = None,
    soyad: Optional[str] = None,
    ad_soyad: Optional[str] = None,
    il: Optional[str] = None
):
    """Mernis sorgula"""
    sonuclar = []
    
    for tc_kayit, bilgi in mernis_data.items():
        eslesme = True
        
        if tc:
            if tc != tc_kayit:
                eslesme = False
        if ad and eslesme:
            # Ad alanı var mı kontrol et
            if "ad" in bilgi:
                if ad.upper() not in bilgi["ad"].upper():
                    eslesme = False
            else:
                eslesme = False
        if soyad and eslesme:
            if soyad.upper() not in bilgi["soyad"].upper():
                eslesme = False
        if ad_soyad and eslesme:
            if "ad" in bilgi:
                tam_ad = f"{bilgi['ad']} {bilgi['soyad']}"
                if ad_soyad.upper() not in tam_ad.upper():
                    eslesme = False
            else:
                eslesme = False
        if il and eslesme:
            if il.upper() not in bilgi["il"].upper():
                eslesme = False
        
        if eslesme:
            sonuclar.append({
                "tc": tc_kayit,
                **bilgi
            })
    
    if not sonuclar:
        return {"bulundu": False, "mesaj": "Mernis kaydı bulunamadı"}
    
    return {"sonuc": len(sonuclar), "kayitlar": sonuclar}

@app.get("/depremzede")
def depremzede_sorgula(
    ad_soyad: Optional[str] = None,
    il: Optional[str] = None,
    poliklinik: Optional[str] = None,
    hastane: Optional[str] = None,
    gelis_sekli: Optional[str] = None
):
    """Depremzede sorgula"""
    sonuclar = []
    
    for kayit in depremzede_data:
        eslesme = True
        
        if ad_soyad:
            if ad_soyad.upper() not in kayit["ad_soyad"].upper():
                eslesme = False
        if il and eslesme:
            if il.upper() not in kayit["il"].upper():
                eslesme = False
        if poliklinik and eslesme:
            if poliklinik.upper() not in kayit["poliklinik"].upper():
                eslesme = False
        if hastane and eslesme:
            if hastane.upper() not in kayit["hastane"].upper():
                eslesme = False
        if gelis_sekli and eslesme:
            if gelis_sekli.upper() not in kayit["gelis_sekli"].upper():
                eslesme = False
        
        if eslesme:
            sonuclar.append(kayit)
    
    if not sonuclar:
        return {"bulundu": False, "mesaj": "Depremzede bulunamadı"}
    
    return {"sonuc": len(sonuclar), "kayitlar": sonuclar}

@app.get("/istatistik")
def istatistik():
    """İstatistik göster"""
    return {
        "mernis_kayit": len(mernis_data),
        "depremzede_kayit": len(depremzede_data),
        "toplam_kayit": len(mernis_data) + len(depremzede_data)
    }

@app.get("/debug/dosyalar")
def debug_dosyalar():
    """Hata ayıklama - Mevcut dosyaları listele"""
    dosyalar = []
    for f in os.listdir("."):
        if f.endswith(".txt"):
            boyut = os.path.getsize(f) if os.path.exists(f) else 0
            dosyalar.append({
                "isim": f,
                "boyut": boyut,
                "var": os.path.exists(f)
            })
    return {"dosyalar": dosyalar}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
