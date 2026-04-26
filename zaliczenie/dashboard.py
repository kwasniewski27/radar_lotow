import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import os

st.set_page_config(page_title="Radar Cen Lotów", layout="wide")

@st.cache_data 
def wczytaj_dane():
    katalog_skryptu = os.path.dirname(os.path.abspath(__file__))
    sciezka_bazy = os.path.join(katalog_skryptu, 'baza_lotow.db')
    con = sqlite3.connect(sciezka_bazy)
    df = pd.read_sql_query("SELECT * FROM loty", con)
    con.close()
    
    df['cena'] = df['cena'].astype(str)
    df['cena'] = df['cena'].str.replace(r'\s+', '', regex=True)
    df['cena'] = df['cena'].str.replace(',', '.')
    df['cena'] = df['cena'].str.replace('zł', '', case=False)
    df['cena'] = df['cena'].str.replace('PLN', '', case=False)
    df['cena'] = df['cena'].str.replace(r'[^\d.]', '', regex=True) 
    df['cena'] = pd.to_numeric(df['cena'], errors='coerce')
    df['data_lotu'] = pd.to_datetime(df['data_lotu'], errors='coerce')
    df['data_sprawdzenia'] = pd.to_datetime(df['data_sprawdzenia'], errors='coerce')
    df = df.dropna(subset=['cena', 'data_lotu', 'data_sprawdzenia'])
    
    df['dni_do_wylotu'] = (df['data_lotu'] - df['data_sprawdzenia']).dt.days
    return df

df = wczytaj_dane()

def generuj_wnioski_ai(df, miasto):
    if len(df) < 10:
        return "Zbyt mało danych, aby wirtualny asystent mógł wyciągnąć wiarygodne wnioski."
    
    min_cena = df['cena'].min()
    srednia_cena = df['cena'].mean()
    oszczednosc = srednia_cena - min_cena
    
    kwantyl_5 = df['cena'].quantile(0.05)
    tanie_loty = df[df['cena'] <= kwantyl_5]
    
    srodek_zlotego_okna = int(tanie_loty['dni_do_wylotu'].median())
    
    tekst = f"🤖 **Wirtualny Analityk:** Przeanalizowałem {len(df)} lotów do {miasto}. Z moich obliczeń wynika, że najtańsze bilety do miasta **{miasto}** (nawet za {min_cena} PLN) pojawiają się zazwyczaj na około **{srodek_zlotego_okna} dni przed wylotem**. Celując w to okienko, oszczędzasz średnio **{int(oszczednosc)} PLN** w stosunku do normalnej ceny. "
    
    if srodek_zlotego_okna < 14:
        tekst += "*Rekomendacja: Na tej trasie opłaca się czekać na Last Minute!*"
    elif srodek_zlotego_okna > 50:
        tekst += "*Rekomendacja: Przewoźnik wyraźnie promuje zakupy z dużym wyprzedzeniem (First Minute). Kupuj wcześnie!*"
    else:
        tekst += "*Rekomendacja: Klasyczny środek sezonu zakupowego. Nie czekaj do ostatniej chwili, ale też nie kupuj z półrocznym wyprzedzeniem.*"
        
    return tekst

# --- SIDEBAR (Panel boczny z pamięcią wyboru) ---
st.sidebar.header("Menu Główne")
max_cena_bazy = int(df['cena'].max())
max_cena = st.sidebar.slider("Maksymalna cena (PLN):", min_value = 0, max_value = max_cena_bazy, value = max_cena_bazy)
st.sidebar.markdown("---")
aktualny_widok = st.query_params.get("widok", "Ekran Główny")
if st.sidebar.button("🏠 Ekran Główny", type="primary", use_container_width=True):
    st.query_params["widok"] = "Ekran Główny"
    st.rerun()
st.sidebar.markdown("### ✈️ Wybierz kierunek:")

# 4. LISTA MIAST
lista_miast = sorted(df['kierunek'].unique().tolist())

# Magiczny trik: jeśli jesteśmy na Ekranie Głównym, lista miast odznacza kropkę (index=None)
startowy_index = lista_miast.index(aktualny_widok) if aktualny_widok in lista_miast else None

wybrane_miasto_radio = st.sidebar.radio(
    "Kierunki:", 
    lista_miast, 
    index=startowy_index,
    label_visibility="collapsed" # Ukrywamy domyślny, mały napis nad listą, bo użyliśmy ładnego Markdowna wyżej
)

# 5. REAKCJA NA WYBÓR MIASTA
if wybrane_miasto_radio and wybrane_miasto_radio != aktualny_widok:
    st.query_params["widok"] = wybrane_miasto_radio
    st.rerun()

# --- GŁÓWNA STRONA ---
if aktualny_widok == "Ekran Główny":
    st.title("Witamy w Radarze Okazji Lotniczych! 🌍")
    st.markdown("""
    Ten zaawansowany system analityczny codziennie monitoruje i zapisuje ceny biletów lotniczych.
    Dzięki zebranym danym, potrafimy przewidzieć, kiedy najlepiej kupić bilet, 
    aby zaoszczędzić najwięcej pieniędzy.
    """)
    
    st.markdown("### 📈 Nasza baza danych w liczbach:")
    
    df_budzet = df[df['cena'] <= max_cena]
    c1, c2, c3 = st.columns(3)
    c1.metric("Zebrane loty", len(df_budzet))
    c2.metric("Monitorowane kierunki", len(lista_miast))
    if not df_budzet.empty:
        c3.metric("Najtańszy lot w systemie", f"{df_budzet['cena'].min()} PLN")
    else:
        c3.metric("Najtańszy lot w systemie", "Brak")
        
    st.info("👈 **Aby rozpocząć, wybierz interesujący Cię kierunek z menu po lewej stronie!**")
    
    st.image("https://images.unsplash.com/photo-1436491865332-7a61a109cc05?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80", 
             use_container_width=True)
else:
    wybrane_miasto = aktualny_widok
    maska = (df['kierunek'] == wybrane_miasto) & (df['cena'] <= max_cena)
    filtered_df = df[maska]
    st.title(f"📊 Analiza lotów do: {wybrane_miasto}")
    if filtered_df.empty:
        st.warning(f"Brak lotów do {wybrane_miasto} poniżej {max_cena} PLN. Spróbuj zwiększyć budżet!")
    else:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Najniższa cena", f"{int(filtered_df['cena'].min())} PLN")
        col2.metric("Najwyższa cena", f"{int(filtered_df['cena'].max())} PLN") 
        col3.metric("Średnia cena", f"{round(filtered_df['cena'].mean(), 2)} PLN")
        col4.metric("Liczba lotów", len(filtered_df))

        st.subheader("📉 Kiedy kupować?")
        st.write("Wykres pokazuje, jak zmieniała się cena w zależności od tego, ile dni zostało do wylotu.")

        fig = px.scatter(filtered_df, 
                    x="dni_do_wylotu", 
                    y="cena", 
                    color="cena", 
                    color_continuous_scale="Viridis",
                    trendline="lowess",
                    trendline_color_override="red", 
                    template="plotly_dark", 
                    labels={"dni_do_wylotu": "Dni do wylotu", "cena": "Cena (PLN)"},
        )
        fig.update_xaxes(autorange="reversed")

        tab1, tab2 = st.tabs(["Złote Okno", "Statystyki Tygodnia"])

        with tab1:
            st.plotly_chart(fig, width="stretch", key="wykres_glowny_viridis")
            st.info("💡 Wskazówka: Linia trendu pokazuje 'Złote Okno'. Jeśli opada w lewo, oznacza to, że im bliżej lotu, tym jest drożej.")
            st.markdown("---") 
            with st.expander("🤖 Zapytaj Wirtualnego Analityka o poradę"):
                wnioski = generuj_wnioski_ai(filtered_df, wybrane_miasto)
                st.success(wnioski) 
        with tab2:
            st.subheader("📅 Statystyki dni tygodnia")
            df_tydzien = df[df['kierunek'] == wybrane_miasto].copy()            
            dni_pl = {'Monday': 'Poniedziałek', 'Tuesday': 'Wtorek', 'Wednesday': 'Środa', 
                    'Thursday': 'Czwartek', 'Friday': 'Piątek', 'Saturday': 'Sobota', 'Sunday': 'Niedziela'}
            
            df_tydzien['dzien_lotu'] = df_tydzien['data_lotu'].dt.day_name().map(dni_pl)
            kolejnosc = ['Poniedziałek', 'Wtorek', 'Środa', 'Czwartek', 'Piątek', 'Sobota', 'Niedziela']
            
            srednie_dni = df_tydzien.groupby('dzien_lotu')['cena'].mean().reindex(kolejnosc).fillna(0).reset_index()
            srednie_dni['etykieta'] = srednie_dni['cena'].apply(lambda x: "Brak lotów" if x == 0 else f"{x:.0f}")
            
            fig_bar = px.bar(srednie_dni, x='dzien_lotu', y='cena', 
                            text='etykieta',
                            color='cena', color_continuous_scale='Teal',
                            labels={'dzien_lotu': 'Dzień wylotu', 'cena': 'Średnia cena (PLN)'})
            
            fig_bar.update_traces(textposition='outside')
            max_cena_wykres = srednie_dni['cena'].max()
            if max_cena_wykres > 0:
                fig_bar.update_layout(yaxis=dict(range=[0, max_cena_wykres * 1.15]))
            st.plotly_chart(fig_bar, width="stretch", key="wykres_slupkowy_dni")

        
