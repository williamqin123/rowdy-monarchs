import sqlite3 as sql
import numpy as np
import pandas as pd
import seaborn as sns
import geopandas as gpd
import geoplot.crs as gcrs
import geoplot as gplt
import matplotlib.pyplot as plt

from PIL import Image
from matplotlib.patches import Patch, Circle

edge_color = "#30011E"
background_color = "#fafafa"

sns.set_style(
    {
        "font.family": "serif",
        "figure.facecolor": background_color,
        "axes.facecolor": background_color,
    }
)

EARLY_PERIOD = (2015, 2019)
LATE_PERIOD = (2020, 2025)

# Path to your SQLite database file
database_path = "scrapers/JourneyNorth/journeynorth_adult.db"
# Connect to the SQLite database
conn = sql.connect(database_path)
# Define your SQL query
query = "SELECT * FROM sightings"
# Read the data into a DataFrame
df = pd.read_sql_query(query, conn)
# Close the database connection
conn.close()
df["date"] = pd.to_datetime(df["date"], format="%m/%d/%y")
# Display the DataFrame
print(df)

# Load the json file with county coordinates
geoData = gpd.read_file(
    "https://raw.githubusercontent.com/holtzy/The-Python-Graph-Gallery/master/static/data/US-counties.geojson"
)
# Make sure the "id" column is an integer
geoData.id = geoData["id"].astype(int)
# Remove Alaska, Hawaii and Puerto Rico.
statesToRemove = ["02", "15", "72"]
geoData = geoData[~geoData.STATE.isin(statesToRemove)]
extent = geoData.total_bounds
print(geoData)

df_total_sightings_then = (
    df[
        (df["date"].dt.year >= EARLY_PERIOD[0])
        & (df["date"].dt.year <= EARLY_PERIOD[-1])
    ]
    .groupby("countyFIPS")["qty"]
    .sum()
)
df_total_sightings_now = (
    df[(df["date"].dt.year >= LATE_PERIOD[0]) & (df["date"].dt.year <= LATE_PERIOD[-1])]
    .groupby("countyFIPS")["qty"]
    .sum()
)
df_sightings_percent_change = (
    100 * (df_total_sightings_now / df_total_sightings_then - 1)
).reset_index()

# for color mapping with 10 different colors
import mapclassify as mc

scheme = mc.Quantiles(df_sightings_percent_change["qty"], k=7)

gdf = geoData.merge(
    df_sightings_percent_change,
    left_on=["id"],  # identifier from geodataframe
    right_on=["countyFIPS"],  # identifier from dataframe
)

# Basic plot with just county outlines
ax = gplt.polyplot(
    geoData,
    linewidth=0.1,
    facecolor="lightgray",
    projection=gcrs.AlbersEqualArea(),
    figsize=(12, 8),
    extent=extent,
)

gplt.choropleth(
    gdf,
    projection=gcrs.AlbersEqualArea(),
    hue="qty",
    scheme=scheme,
    cmap="bwr",
    linewidth=0.1,
    edgecolor="white",
    legend=True,
    ax=ax,
    extent=extent,
)
ax.set_axis_off()
legend = ax.get_legend()

legend.texts[0].set_text(
    "≤"
    + legend.texts[0].get_text()[
        legend.texts[-1].get_text().index(" - ") + 2 :
    ]  # hides the 0 value
)
legend.texts[-1].set_text(
    legend.texts[-1].get_text()[: legend.texts[-1].get_text().index(" - ")]
    + "+"  # hides the maximum value
)

plt.savefig(f"vis/exports/sightings_deltas_map_percentages.png")

#

df_mean_sightings_then = (
    df[
        (df["date"].dt.year >= EARLY_PERIOD[0])
        & (df["date"].dt.year <= EARLY_PERIOD[-1])
    ]
    .groupby("countyFIPS")["qty"]
    .mean()
)
df_mean_sightings_now = (
    df[(df["date"].dt.year >= LATE_PERIOD[0]) & (df["date"].dt.year <= LATE_PERIOD[-1])]
    .groupby("countyFIPS")["qty"]
    .mean()
)
df_sightings_cohens_d = (
    (
        (df_mean_sightings_now - df_mean_sightings_then)
        / (
            df[
                (df["date"].dt.year >= EARLY_PERIOD[0])
                & (df["date"].dt.year <= EARLY_PERIOD[-1])
            ]
            .groupby("countyFIPS")["qty"]
            .std()
        )
    )
    .fillna(0)
    .reset_index()
)

scheme = mc.Quantiles(df_sightings_cohens_d["qty"], k=7)

gdf = geoData.merge(
    df_sightings_cohens_d,
    left_on=["id"],  # identifier from geodataframe
    right_on=["countyFIPS"],  # identifier from dataframe
)

# Basic plot with just county outlines
ax = gplt.polyplot(
    geoData,
    linewidth=0.1,
    facecolor="lightgray",
    projection=gcrs.AlbersEqualArea(),
    figsize=(12, 8),
    extent=extent,
)

gplt.choropleth(
    gdf,
    projection=gcrs.AlbersEqualArea(),
    hue="qty",
    scheme=scheme,
    cmap="bwr",
    linewidth=0.1,
    edgecolor="white",
    legend=True,
    ax=ax,
    extent=extent,
)
ax.set_axis_off()
legend = ax.get_legend()

legend.texts[0].set_text(
    "≤"
    + legend.texts[0].get_text()[
        legend.texts[-1].get_text().index(" - ") + 2 :
    ]  # hides the 0 value
)
legend.texts[-1].set_text(
    legend.texts[-1].get_text()[: legend.texts[-1].get_text().index(" - ")]
    + "+"  # hides the maximum value
)

plt.title(
    f"Mean Cohen’s d = {df_sightings_cohens_d[(df_sightings_cohens_d['qty'] != 0) & (~np.isnan(df_sightings_cohens_d['qty'])) & (~(df_sightings_cohens_d['qty'].isnull()))].fillna(0)['qty'].mean()}"
)

plt.savefig(f"vis/exports/sightings_deltas_map_cohens_d.png")
