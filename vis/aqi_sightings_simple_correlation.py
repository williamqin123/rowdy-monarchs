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

#

# Specify the path to your CSV file
file_path = (
    "scrapers/AirQualityEPA/cleaned_aqi_data.csv"  # Replace with your actual file path
)

# Read the CSV file into a DataFrame with additional options
df_aqi = pd.read_csv(
    file_path,
    sep=",",
    header=0,
    index_col=None,
    usecols=[
        "State",
        "County",
        "Year",
        "Days with AQI",
        "Good Days",
        "Moderate Days",
        "Unhealthy for Sensitive Groups Days",
        "Unhealthy Days",
        "Very Unhealthy Days",
        "Hazardous Days",
        "Max AQI",
        "90th Percentile AQI",
        "Median AQI",
        "Days CO",
        "Days NO2",
        "Days Ozone",
        "Days PM2.5",
        "Days PM10",
    ],
)

import addfips

af = addfips.AddFIPS()
col = []
for index, row in df_aqi.iterrows():
    af.add_county_fips(row, "County", "State")
    # print(row)
    col.append(int(row["fips"]) if not (row["fips"] is None) else None)
df_aqi["fips"] = col
df_aqi = df_aqi[~(df_aqi["fips"].isnull())]
df_aqi["fips"] = df_aqi["fips"].astype(int)

# Display the DataFrame
print(df_aqi)

#

# Path to your SQLite database file
database_path = "scrapers/JourneyNorth/journeynorth_adult.db"
# Connect to the SQLite database
conn = sql.connect(database_path)
# Define your SQL query
query = "SELECT * FROM sightings"
# Read the data into a DataFrame
df_sights_adults = pd.read_sql_query(query, conn)
# Close the database connection
conn.close()
# Display the DataFrame
print(df_sights_adults)
df_sights_adults["date"] = pd.to_datetime(df_sights_adults["date"], format="%m/%d/%y")
q = df_sights_adults["qty"].quantile(
    0.999
)  # top 0.1% of entered quatities = possible trolls
df_no_outliers = df_sights_adults[
    df_sights_adults["qty"] < q
]  # excludes top 0.1% of entered quantities]

#

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

# for color mapping with 10 different colors
import mapclassify as mc

#

df = df_aqi.merge(df_sights_adults, left_on=["fips"], right_on=["countyFIPS"])

# cross-correlation
corrcoefs = []
for index, row in df.iterrows():
    np.correlate(
        df.groupby("fips")["Median AQI"].to_numpy(),
        df.groupby("fips")["qty"].to_numpy(),
    )
df["corrcoeff"] = corrcoefs

gdf = geoData.merge(
    df,
    left_on=["id"],  # identifier from geodataframe
    right_on=["fips"],  # identifier from dataframe
)

scheme = mc.Quantiles(
    df["corrcoeff"],
    k=11,
)

#

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
    hue="corrcoeff",
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

plt.savefig(f"vis/exports/basic_pearsons_R.png")
