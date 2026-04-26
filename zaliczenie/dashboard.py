import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

st.set_page_config(page_title="Radar Cen Lotów", layout="wide")

@st.cache_data 
def wczytaj_dane():
    con = sqlite3.connect('baza_lotow.db')
    df = pd.read_sql_query("SELECT * FROM loty", con)
    con.close()
    
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
    
    tekst = f"🤖 **Wirtualny Analityk:** Przeanalizowałem {len(df)} lotów. Z moich obliczeń wynika, że najtańsze bilety do miasta **{miasto}** (nawet za {min_cena} PLN) pojawiają się zazwyczaj na około **{srodek_zlotego_okna} dni przed wylotem**. Celując w to okienko, oszczędzasz średnio **{int(oszczednosc)} PLN** w stosunku do normalnej ceny. "
    
    if srodek_zlotego_okna < 14:
        tekst += "*Rekomendacja: Na tej trasie opłaca się czekać na Last Minute!*"
    elif srodek_zlotego_okna > 50:
        tekst += "*Rekomendacja: Przewoźnik wyraźnie promuje zakupy z dużym wyprzedzeniem (First Minute). Kupuj wcześnie!*"
    else:
        tekst += "*Rekomendacja: Klasyczny środek sezonu zakupowego. Nie czekaj do ostatniej chwili, ale też nie kupuj z półrocznym wyprzedzeniem.*"
        
    return tekst

st.sidebar.header("Filtry")

lista_miast = sorted(df['kierunek'].unique().tolist())

wybor_z_url = st.query_params.get("miasto")

if wybor_z_url in lista_miast:
    startowe_miasto = wybor_z_url
elif "Manchester" in lista_miast:
    startowe_miasto = "Manchester"
else:
    startowe_miasto = lista_miast[0]

startowy_index = lista_miast.index(startowe_miasto)

wybrane_miasto = st.sidebar.radio(
    "Wybierz kierunek:", 
    lista_miast, 
    index=startowy_index,
    format_func=lambda miasto: f"✈️ {miasto}"
)

st.query_params["miasto"] = wybrane_miasto

max_cena = st.sidebar.slider("Maksymalna cena (PLN):", 0, int(df['cena'].max()), 999)

maska = (df['kierunek'] == wybrane_miasto) & (df['cena'] <= max_cena)
filtered_df = df[maska]

st.title(f"📊 Analiza lotów do: {wybrane_miasto}")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Najniższa cena", f"{filtered_df['cena'].min()} PLN")
col2.metric("Najwyższa cena", f"{filtered_df['cena'].max()} PLN") # TUTAJ JEST NOWY KAFELEK
col3.metric("Średnia cena", f"{round(filtered_df['cena'].mean(), 2)} PLN")
col4.metric("Liczba przeanalizowanych lotów", len(filtered_df))

st.subheader("📉 Kiedy kupować?")
st.write("Wykres pokazuje, jak zmieniała się cena w zależności od tego, ile dni zostało do wylotu.")

fig = px.scatter(filtered_df, 
                 x="dni_do_wylotu", 
                 y="cena", 
                 color="cena", # Kolor kropek będzie zależał od ceny (od niebieskiego do czerwonego)
                 color_continuous_scale="Viridis", # Piękna paleta kolorów
                 trendline="lowess",
                 trendline_color_override="red", # Czerwona, gruba linia trendu
                 template="plotly_dark", # Mroczny motyw wykresu
                 labels={"dni_do_wylotu": "Dni do wylotu", "cena": "Cena (PLN)"},
)
fig.update_xaxes(autorange="reversed")

tab1, tab2 = st.tabs(["Złote Okno", "Statystyki Tygodnia"])

with tab1:
    # Rysujemy wykres TYLKO RAZ wewnątrz zakładki
    st.plotly_chart(fig, width="stretch", key="wykres_glowny_viridis")
    st.info("💡 Wskazówka: Linia trendu pokazuje 'Złote Okno'. Jeśli opada w lewo, oznacza to, że im bliżej lotu, tym jest drożej.")
    

    st.markdown("---") 
    with st.expander("🤖 Zapytaj Wirtualnego Analityka o poradę"):
        wnioski = generuj_wnioski_ai(filtered_df, wybrane_miasto)
        st.success(wnioski) 
with tab2:
    st.subheader("📅 Kiedy najtaniej lecieć?")
    st.write("Linie lotnicze często zmieniają ceny w zależności od dnia tygodnia. Sprawdźmy, w które dni wylot opłaca się najbardziej!")
    
    df_tydzien = filtered_df.copy()
    
    dni_pl = {'Monday': 'Poniedziałek', 'Tuesday': 'Wtorek', 'Wednesday': 'Środa', 
              'Thursday': 'Czwartek', 'Friday': 'Piątek', 'Saturday': 'Sobota', 'Sunday': 'Niedziela'}
              
    df_tydzien['dzien_lotu'] = df_tydzien['data_lotu'].dt.day_name().map(dni_pl)
    
    kolejnosc = ['Poniedziałek', 'Wtorek', 'Środa', 'Czwartek', 'Piątek', 'Sobota', 'Niedziela']
    
    srednie_dni = df_tydzien.groupby('dzien_lotu')['cena'].mean().reindex(kolejnosc).reset_index()
    
    puste_dni = srednie_dni[srednie_dni['cena'].isna()]['dzien_lotu'].tolist()
    
        
    srednie_dni = df_tydzien.groupby('dzien_lotu')['cena'].mean().reindex(kolejnosc).reset_index()
    
    srednie_dni['cena'] = srednie_dni['cena'].fillna(0)
    
    srednie_dni['etykieta'] = srednie_dni['cena'].apply(lambda x: "Brak lotów" if x == 0 else f"{x:.0f}")
    
    fig_bar = px.bar(srednie_dni, x='dzien_lotu', y='cena', 
                     text='etykieta',
                     color='cena', color_continuous_scale='Teal',
                     labels={'dzien_lotu': 'Dzień wylotu', 'cena': 'Średnia cena (PLN)'},
                     title="Średnia cena biletu wg dnia wylotu")
    
    fig_bar.update_traces(textposition='outside')
    
    max_cena_wykres = srednie_dni['cena'].max()
    if max_cena_wykres > 0:
        fig_bar.update_layout(yaxis=dict(range=[0, max_cena_wykres * 1.15]))
    
    st.plotly_chart(fig_bar, width="stretch", key="wykres_slupkowy_dni_etykiety")