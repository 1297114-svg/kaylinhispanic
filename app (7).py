import datetime
import io

import matplotlib.pyplot as plt
import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="Hispanic Heritage Historical Data Explorer", page_icon="🌎", layout="wide")

# Hispanic Heritage-inspired decoration
st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #fff8e8 0%, #fff 55%, #eef8ff 100%); }
.hero {
  padding: 1.35rem 1.5rem; border-radius: 18px; color: white;
  background: linear-gradient(100deg, #b91c1c, #e87920, #15803d, #1d4ed8);
  margin-bottom: 1rem;
}
.hero h1 { color: white; margin: 0; }
.hero p { color: white; margin: .4rem 0 0; }
div[data-testid="stMetric"] { background: white; padding: 12px; border-radius: 12px; border: 1px solid #eee; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
<h1>🌎 Hispanic Heritage Historical Data Explorer</h1>
<p>Explore real historical indicators from the World Bank • Cultura · Historia · Datos</p>
</div>
""", unsafe_allow_html=True)

# Country names map to World Bank ISO-3 codes.
HISPANIC_COUNTRIES = {
    "Argentina": "ARG",
    "Bolivia": "BOL",
    "Chile": "CHL",
    "Colombia": "COL",
    "Costa Rica": "CRI",
    "Cuba": "CUB",
    "Dominican Republic": "DOM",
    "Ecuador": "ECU",
    "El Salvador": "SLV",
    "Equatorial Guinea": "GNQ",
    "Guatemala": "GTM",
    "Honduras": "HND",
    "Mexico": "MEX",
    "Nicaragua": "NIC",
    "Panama": "PAN",
    "Paraguay": "PRY",
    "Peru": "PER",
    "Spain": "ESP",
    "Uruguay": "URY",
    "Venezuela": "VEN",
}
# Brazil is Portuguese-speaking and is included only as a Latin American comparison.
COMPARISON_COUNTRIES = {"Brazil (Latin American comparison)": "BRA"}

INDICATORS = {
    "Life expectancy at birth": ("SP.DYN.LE00.IN", "years", "Average number of years a newborn is expected to live under current mortality patterns."),
    "Unemployment, national estimate": ("SL.UEM.TOTL.NE.ZS", "% of labor force", "Share of the labor force that is unemployed, using national estimates."),
    "GDP per capita": ("NY.GDP.PCAP.CD", "current US$", "Gross domestic product divided by the population. It is not average wealth or household income."),
    "Crude birth rate": ("SP.DYN.CBRT.IN", "births per 1,000 people", "Annual live births per 1,000 people; this is a rate, not a birth count."),
    "Net migration": ("SM.POP.NETM", "people", "Net number of migrants; it is not an emigration count."),
    "Intentional homicide rate": ("VC.IHR.PSRC.P5", "per 100,000 people", "Intentional homicides per 100,000 people."),
    "Consumer price inflation": ("FP.CPI.TOTL.ZG", "% annual", "Annual percentage change in consumer prices."),
    "Central government debt": ("GC.DOD.TOTL.GD.ZS", "% of GDP", "Central government debt as a percentage of GDP."),
    "Total reserves including gold": ("FI.RES.TOTL.CD", "current US$", "Total reserves including gold, reported in current US dollars."),
    "External balance on goods and services": ("NE.RSB.GNFS.ZS", "% of GDP", "External balance on goods and services as a percentage of GDP."),
}

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_world_bank(country_code: str, indicator_code: str, start_year: int, end_year: int) -> pd.DataFrame:
    url = (
        f"https://api.worldbank.org/v2/country/{country_code}/indicator/"
        f"{indicator_code}?format=json&date={start_year}:{end_year}&per_page=200"
    )
    response = requests.get(url, timeout=20)
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, list) or len(payload) < 2 or not payload[1]:
        return pd.DataFrame(columns=["Year", "Value"])
    records = [
        {"Year": int(item["date"]), "Value": item["value"]}
        for item in payload[1]
        if item.get("date") and item.get("value") is not None
    ]
    if not records:
        return pd.DataFrame(columns=["Year", "Value"])
    return pd.DataFrame(records).sort_values("Year").reset_index(drop=True)

today_year = datetime.date.today().year
start_year = today_year - 70
end_year = today_year - 1

with st.sidebar:
    st.header("🔎 Explore")
    selected_country = st.selectbox("Hispanic country", list(HISPANIC_COUNTRIES.keys()), index=12)
    include_brazil = st.checkbox("Include Brazil as a comparison", value=False)
    indicator_name = st.selectbox("Historical indicator", list(INDICATORS.keys()))
    st.caption(f"Years requested: {start_year}–{end_year}")
    st.caption("Data source: World Bank API")

indicator_code, units, definition = INDICATORS[indicator_name]
country_code = HISPANIC_COUNTRIES[selected_country]

st.subheader(f"📊 {selected_country}: {indicator_name}")
st.write(f"**Definition:** {definition}")
st.write(f"**Units:** {units}")
st.markdown("[Open the World Bank API source](https://api.worldbank.org/)")

try:
    with st.spinner("Retrieving official World Bank data…"):
        data = fetch_world_bank(country_code, indicator_code, start_year, end_year)
    if data.empty:
        st.warning("The World Bank API returned no non-null observations for this selection.")
    else:
        data["Year"] = data["Year"].astype(int)
        data["Value"] = pd.to_numeric(data["Value"], errors="coerce")
        data = data.dropna(subset=["Value"]).sort_values("Year")
        st.caption(
            f"Retrieved {len(data)} observations • Coverage: {data['Year'].min()}–{data['Year'].max()} • "
            f"Retrieved on {datetime.date.today().isoformat()}"
        )
        c1, c2, c3 = st.columns(3)
        c1.metric("Observations", f"{len(data)}")
        c2.metric("First available year", f"{data['Year'].min()}")
        c3.metric("Latest available year", f"{data['Year'].max()}")

        fig, ax = plt.subplots(figsize=(10, 4.8))
        ax.plot(data["Year"], data["Value"], marker="o", linewidth=2, label=selected_country)
        ax.set_xlabel("Year")
        ax.set_ylabel(units)
        ax.set_title(f"{indicator_name} — {selected_country}")
        ax.grid(True, alpha=0.25)
        ax.legend()
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

        if include_brazil:
            try:
                brazil = fetch_world_bank("BRA", indicator_code, start_year, end_year)
                if not brazil.empty:
                    fig2, ax2 = plt.subplots(figsize=(10, 4.8))
                    ax2.plot(data["Year"], data["Value"], marker="o", label=selected_country)
                    ax2.plot(brazil["Year"], brazil["Value"], marker="s", label="Brazil (comparison)")
                    ax2.set_xlabel("Year")
                    ax2.set_ylabel(units)
                    ax2.set_title(f"Country comparison — {indicator_name}")
                    ax2.grid(True, alpha=0.25)
                    ax2.legend()
                    st.pyplot(fig2, use_container_width=True)
                    plt.close(fig2)
                else:
                    st.info("Brazil has no non-null observations for this indicator and period.")
            except requests.RequestException as exc:
                st.warning(f"Could not retrieve Brazil comparison data: {exc}")

        st.subheader("Data table")
        st.dataframe(data, use_container_width=True, hide_index=True)
        csv_bytes = data.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download data as CSV",
            data=csv_bytes,
            file_name=f"{country_code}_{indicator_code}_{start_year}_{end_year}.csv",
            mime="text/csv",
        )
except (requests.RequestException, ValueError, TypeError) as exc:
    st.error(f"Unable to retrieve or read World Bank data. Check your internet connection and try again. Details: {exc}")

st.markdown("---")
st.caption("Hispanic Heritage Data Lab • Historical observations are sourced from the World Bank. Missing values are not fabricated.")
