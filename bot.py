def load_depremzede():
    """Depremzede verilerini yükle - Sıra,"AD SOYAD","POLİKLİNİK","HASTANE","GELİŞ ŞEKLİ","İL" """
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
                
                # Virgül ile ayır
                parts = line.split(",")
                if len(parts) < 5:
                    continue
                
                # Tırnakları temizle
                ad_soyad = parts[1].strip().strip('"')
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
            
            print(f"✅ Depremzede: {satir_sayisi} satır okundu, {len(data)} kayıt yüklendi")
            
    except Exception as e:
        print(f"❌ {dosya_adi} okunurken hata: {e}")
    
    return data

def load_mernis():
    """Mernis verilerini yükle - TC|ADRES|SOYAD|İL"""
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
                    
                data[tc] = {
                    "adres": parts[1].strip() if len(parts) > 1 else "",
                    "soyad": parts[2].strip() if len(parts) > 2 else "",
                    "il": parts[3].strip() if len(parts) > 3 else ""
                }
                satir_sayisi += 1
            
            print(f"✅ Mernis: {satir_sayisi} satır okundu, {len(data)} kayıt yüklendi")
            
    except Exception as e:
        print(f"❌ {dosya_adi} okunurken hata: {e}")
    
    return data
