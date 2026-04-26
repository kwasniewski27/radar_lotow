import json
from datetime import datetime

# 1. Sprawdzamy dzisiejszą datę (tak samo jak w pająku)
dzisiaj = datetime.now().strftime("%Y-%m-%d")
plik_json = f"loty_{dzisiaj}.json"
plik_txt = f"posortowane_loty_{dzisiaj}.txt"

try:
    # 2. Wczytujemy dzisiejszy plik JSON
    with open(plik_json, encoding='utf-8') as f:
        loty = json.load(f)

    wyniki = {}

    # 3. Grupujemy
    for lot in loty:
        kierunek = lot.get('kierunek')
        if not kierunek:
            continue
        data = lot.get('data') or "brak daty"
        cena = lot.get('cena') or "brak ceny"
        waluta = lot.get('waluta') or "brak waluty"
    
        detale = f"{data} {cena}{waluta}"
        wyniki.setdefault(kierunek, []).append(detale)

    # 4. Zapisujemy do dzisiejszego pliku TXT
    with open(plik_txt, 'w', encoding='utf-8') as plik_wyjsciowy:
        for kierunek in sorted(wyniki):
            posortowane_loty = sorted(wyniki[kierunek])
            plik_wyjsciowy.write(f"{kierunek}:\n")
            for lot_detal in posortowane_loty:
                plik_wyjsciowy.write(f"  - {lot_detal}\n")
            plik_wyjsciowy.write("\n")
            linijka = f"{kierunek}: - {', '.join(wyniki[kierunek])}\n"
            plik_wyjsciowy.write(linijka)

    print(f"Sukces! Wyniki posortowane i zapisane w pliku: {plik_txt}")

except FileNotFoundError:
    print(f"Błąd: Nie znaleziono dzisiejszego pliku {plik_json}. Czy pająk na pewno skończył pracę?")