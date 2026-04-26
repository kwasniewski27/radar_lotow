import pandas as pd
import sqlite3

print("Łączę się z bazą danych...\n")

try:
    con = sqlite3.connect('baza_lotow.db')
    
    df = pd.read_sql_query("SELECT * FROM loty", con)
    
    con.close()

    df = df.dropna(subset=['cena', 'kierunek'])
    
    df['cena'] = pd.to_numeric(df['cena'], errors='coerce')
    
    df['data_lotu'] = pd.to_datetime(df['data_lotu'])

    print("=== RAPORT: ŁOWCA OKAZJI ===")
    print(f"Baza zawiera łącznie {len(df)} rekordów!\n")

    print("🏆 TOP 5 NAJTAŃSZYCH LOTÓW:")
    najtansze = df.sort_values(by='cena').head(5)
    for index, wiersz in najtansze.iterrows():
        data_lotu = wiersz['data_lotu'].strftime('%Y-%m-%d')
        print(f"✈️  {wiersz['kierunek']} | {data_lotu} | {wiersz['cena']} {wiersz['waluta']} (Sprawdzono: {wiersz['data_sprawdzenia']})")
    
    print("\n-----------------------------------\n")

    print("📊 ŚREDNIA CENA LOTU DO DANEGO MIASTA:")
    srednie_ceny = df.groupby('kierunek')['cena'].mean().round(2).sort_values()
    print(srednie_ceny.head(10).to_string()) # Pokazuje 10 najtańszych miast
    
    print("\n-----------------------------------\n")
    
    miasto = "Marrakesz" # <-- Tu możesz wpisać dowolne miasto ze swojej bazy
    print(f"💡 NAJTAŃSZY LOT DLA KONKRETNEGO MIASTA ({miasto}):")
    
    loty_wybrane = df[df['kierunek'] == miasto]
    
    if not loty_wybrane.empty:
        najtanszy_wybrany = loty_wybrane.loc[loty_wybrane['cena'].idxmin()]
        data_lotu = najtanszy_wybrany['data_lotu'].strftime('%Y-%m-%d')
        print(f"🎯 NAJLEPSZA OKAZJA DO {miasto.upper()}:")
        print(f"Data lotu: {data_lotu} | Cena: {najtanszy_wybrany['cena']} {najtanszy_wybrany['waluta']} | Sprawdzono: {najtanszy_wybrany['data_sprawdzenia']}")
    else:
        print(f"Brak danych dla miasta: {miasto}")

except sqlite3.OperationalError:
    print("Błąd: Nie potrafię połączyć się z bazą 'baza_lotow.db'. Czy plik analizy leży w tym samym folderze co baza?")
except Exception as e:
    print(f"Wystąpił nieoczekiwany błąd: {e}")