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
database_path = "../data/AirQualityEPA.db"
# Connect to the SQLite database
conn = sql.connect(database_path)
# Define your SQL query
query = "SELECT * FROM quarterlySummaries"
# Read the data into a DataFrame
df = pd.read_sql_query(query, conn)
# Close the database connection
conn.close()

import addfips

af = addfips.AddFIPS()
col = []
for index, row in df.iterrows():
    af.add_county_fips(row, "county", "state")
    # print(row)
    col.append(int(row["fips"]) if not (row["fips"] is None) else None)
df["fips"] = col
df = df[~(df["fips"].isnull())]
df["fips"] = df["fips"].astype(int)

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

df_mean_temp = df[df["parameter"] == "Temperature"]

df_mean_temp_then = (
    df_mean_temp[
        (df_mean_temp["year"] >= EARLY_PERIOD[0])
        & (df_mean_temp["year"] <= EARLY_PERIOD[-1])
    ]
    .groupby("fips")["arithmeticMeanValue"]
    .mean()
)
df_mean_temp_now = (
    df_mean_temp[
        (df_mean_temp["year"] >= LATE_PERIOD[0])
        & (df_mean_temp["year"] <= LATE_PERIOD[-1])
    ]
    .groupby("fips")["arithmeticMeanValue"]
    .mean()
)
df_mean_temp_diff = (df_mean_temp_now - df_mean_temp_then).reset_index()

# for color mapping with 10 different colors
import mapclassify as mc

scheme = mc.Quantiles(df_mean_temp_diff["arithmeticMeanValue"], k=7)

gdf = geoData.merge(
    df_mean_temp_diff,
    left_on=["id"],  # identifier from geodataframe
    right_on=["fips"],  # identifier from dataframe
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
    hue="arithmeticMeanValue",
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
        legend.texts[-1].get_text().index("-") + 1 :
    ]  # hides the 0 value
)
legend.texts[-1].set_text(
    legend.texts[-1].get_text()[: legend.texts[-1].get_text().index(" -")]
    + "+"  # hides the maximum value
)

"""
plt.title(
    f"σ 2015–2019 (Quarterly) = {df_mean_temp_then['arithmeticMeanValue'].std()}\nσ 2020–2024 (Quarterly) = {df_mean_temp_now['arithmeticMeanValue'].std()}\nCohen’s d = {df_mean_temp_diff['arithmeticMeanValue'].mean() / df_mean_temp_then['arithmeticMeanValue'].std()}"
)
"""

plt.savefig(f"vis/exports/climate_deltas_cohens_d.png")
