import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="Energy & Emissions Dashboard", layout="wide")
sns.set_theme(style="whitegrid")

st.title("🌍 Energy & Emissions Dashboard")
st.markdown("Understanding the relationship between energy use, renewables, and CO₂ emissions")

# =========================
# LOAD DATA
# =========================
emissions_raw = pd.read_csv("data/eurostat_emissions.csv")
renewables_raw = pd.read_csv("data/eurostat_renewables.csv")
energy_raw = pd.read_csv("data/eurostat_energy.csv")

# =========================
# CLEAN EUROSTAT DATA
# =========================
def clean_eurostat(df, value_name):
    df = df.rename(columns={
        "geo": "country",
        "TIME_PERIOD": "year",
        "OBS_VALUE": value_name
    })
    df = df[["country", "year", value_name]]
    df["year"] = df["year"].astype(int)
    df = df.dropna()
    return df

emissions = clean_eurostat(emissions_raw, "emissions")
renewables = clean_eurostat(renewables_raw, "renewables")
energy = clean_eurostat(energy_raw, "energy")

# =========================
# SIDEBAR FILTERS
# =========================
st.sidebar.header("🎛 Filters")

countries = sorted(emissions["country"].unique())
selected_country = st.sidebar.selectbox("Select Country", countries)

min_year = max(
    emissions.year.min(),
    renewables.year.min(),
    energy.year.min()
)
max_year = min(
    emissions.year.max(),
    renewables.year.max(),
    energy.year.max()
)

year_range = st.sidebar.slider(
    "Select Year Range",
    int(min_year),
    int(max_year),
    (int(min_year), int(max_year))
)

# =========================
# FILTER DATA
# =========================
emi_f = emissions.query("country == @selected_country and year >= @year_range[0] and year <= @year_range[1]")
ren_f = renewables.query("country == @selected_country and year >= @year_range[0] and year <= @year_range[1]")
ene_f = energy.query("country == @selected_country and year >= @year_range[0] and year <= @year_range[1]")

# =========================
# TIME SERIES PLOTS
# =========================
st.subheader(f"📌 {selected_country} Trends")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### CO₂ Emissions")
    fig, ax = plt.subplots()
    sns.lineplot(data=emi_f, x="year", y="emissions", marker="o", ax=ax)
    ax.set_ylabel("Emissions")
    st.pyplot(fig)

with col2:
    st.markdown("### Renewable Energy Share")
    fig, ax = plt.subplots()
    sns.lineplot(data=ren_f, x="year", y="renewables", marker="o", color="green", ax=ax)
    ax.set_ylabel("Renewables (%)")
    st.pyplot(fig)

with col3:
    st.markdown("### Energy Consumption")
    fig, ax = plt.subplots()
    sns.lineplot(data=ene_f, x="year", y="energy", marker="o", color="orange", ax=ax)
    ax.set_ylabel("Energy Use")
    st.pyplot(fig)

# =========================
# MERGE FOR RELATIONSHIPS
# =========================
scatter_df = (
    emi_f
    .merge(ren_f, on=["country", "year"], how="inner")
    .merge(ene_f, on=["country", "year"], how="inner")
)

# =========================
# RELATIONSHIP PLOTS (IMPROVED)
# =========================
st.subheader("🔍 Energy–Emissions Relationships")

col4, col5 = st.columns(2)

# Renewables vs Emissions
with col4:
    st.markdown("### Renewables vs Emissions")
    fig, ax = plt.subplots()
    sns.scatterplot(
        data=scatter_df,
        x="renewables",
        y="emissions",
        hue="year",
        palette="viridis",
        ax=ax
    )
    sns.regplot(
        data=scatter_df,
        x="renewables",
        y="emissions",
        scatter=False,
        color="red",
        ax=ax
    )
    ax.set_xlabel("Renewables (%)")
    ax.set_ylabel("Emissions")
    st.pyplot(fig)

# Energy vs Emissions
with col5:
    st.markdown("### Energy Consumption vs Emissions")
    fig, ax = plt.subplots()
    sns.scatterplot(
        data=scatter_df,
        x="energy",
        y="emissions",
        hue="year",
        palette="plasma",
        ax=ax
    )
    sns.regplot(
        data=scatter_df,
        x="energy",
        y="emissions",
        scatter=False,
        color="red",
        ax=ax
    )
    ax.set_xlabel("Energy Consumption")
    ax.set_ylabel("Emissions")
    st.pyplot(fig)

# =========================
# COMPARISON PLOT
# =========================
st.subheader("🌍 Top Emitting Countries")

top_emitters = (
    emissions.groupby("country")["emissions"]
    .mean()
    .sort_values(ascending=False)
    .head(10)
)

fig, ax = plt.subplots(figsize=(8,4))
top_emitters.plot(kind="bar", ax=ax)
ax.set_ylabel("Average CO₂ Emissions")
st.pyplot(fig)

# =========================
# CORRELATION HEATMAP
# =========================
st.subheader("📊 Correlation Overview")

fig, ax = plt.subplots(figsize=(5,4))
sns.heatmap(
    scatter_df[["emissions", "renewables", "energy"]].corr(),
    annot=True,
    cmap="coolwarm",
    ax=ax
)
st.pyplot(fig)

# =========================
# FOOTER
# =========================
st.caption("📊 Source: Eurostat | Streamlit Dashboard")



