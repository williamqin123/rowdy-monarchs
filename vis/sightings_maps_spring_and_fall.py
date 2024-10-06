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

# Display the DataFrame
print(df)

df["date"] = pd.to_datetime(df["date"], format="%m/%d/%y")

q = df["qty"].quantile(0.999)  # top 0.1% of entered quatities = possible trolls
df_no_outliers = df[df["qty"] < q]  # excludes top 0.1% of entered quantities

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

fullData = (
    df_no_outliers.groupby(
        [df_no_outliers["date"].map(lambda x: x.year), "countyFIPS"]
    )["qty"]
    .sum()
    .reset_index()
)
fullData = geoData.merge(
    fullData,
    left_on=["id"],  # identifier from geodataframe
    right_on=["countyFIPS"],  # identifier from dataframe
)
print(fullData)

# for color mapping with 10 different colors
import mapclassify as mc

scheme = mc.Quantiles(fullData["qty"], k=10)

for y in range(1996, 2025):
    df_this_year = fullData[(fullData["date"] == y)]

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
        df_this_year,
        projection=gcrs.AlbersEqualArea(),
        hue="qty",
        scheme=scheme,
        cmap="inferno_r",
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

    # plt.colorbar()
    plt.savefig(f"vis/exports/counties_annual_frames/{y}.png")
