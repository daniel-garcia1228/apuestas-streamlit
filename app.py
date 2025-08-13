import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# ==================== CONFIG ====================
API_KEY = "d8c63ad20d38e9f990e5c12b6fe3fa15"
REGION = "us"
MARKETS = "h2h,spreads,totals"
# =================================================

st.set_page_config(page_title="Apuestas Deportivas", layout="wide")
st.title("📊 Analizador de Apuestas Deportivas (The Odds API)")

@st.cache_data(ttl=300)
def get_sports():
    url = f"https://api.the-odds-api.com/v4/sports/?apiKey={API_KEY}"
    r = requests.get(url)
    if r.status_code != 200:
        st.error(f"Error al obtener ligas: {r.text}")
        return []
    return r.json()

@st.cache_data(ttl=300)
def get_odds(sport_key):
    url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds/?apiKey={API_KEY}&regions={REGION}&markets={MARKETS}"
    r = requests.get(url)
    if r.status_code != 200:
        st.warning(f"No se pudo obtener datos para {sport_key}")
        return []
    return r.json()

# Obtener lista de ligas
sports = get_sports()
if not sports:
    st.stop()

# Selección de ligas
sport_options = {sport["title"]: sport["key"] for sport in sports}
selected_sports = st.multiselect("Selecciona ligas", list(sport_options.keys()), default=[])

if st.button("🔄 Actualizar datos") and selected_sports:
    for s in selected_sports:
        get_odds.clear()  # limpiar cache

if selected_sports:
    for league_name in selected_sports:
        st.subheader(f"🏟 {league_name}")
        data = get_odds(sport_options[league_name])
        if not data:
            st.info("No hay partidos próximos")
            continue

        rows = []
        for event in data:
            match_time = datetime.fromisoformat(event["commence_time"].replace("Z", "+00:00"))
            home_team = event["home_team"]
            away_team = event["away_team"]

            for bookmaker in event.get("bookmakers", []):
                book_name = bookmaker["title"]
                for market in bookmaker.get("markets", []):
                    market_type = market["key"]
                    for outcome in market.get("outcomes", []):
                        rows.append({
                            "Fecha/Hora": match_time,
                            "Local": home_team,
                            "Visitante": away_team,
                            "Casa de apuestas": book_name,
                            "Mercado": market_type,
                            "Equipo/Línea": outcome.get("name", ""),
                            "Cuota": outcome.get("price", ""),
                            "Puntos": outcome.get("point", "")
                        })

        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True)
else:
    st.info("Selecciona una o más ligas para ver las cuotas.")
