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
df = pd.read_csv(
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
for index, row in df.iterrows():
    af.add_county_fips(row, "County", "State")
    # print(row)
    col.append(int(row["fips"]) if not (row["fips"] is None) else None)
df["fips"] = col
df = df[~(df["fips"].isnull())]
df["fips"] = df["fips"].astype(int)

# Display the DataFrame
print(df)

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

gdf = geoData.merge(
    df,
    left_on=["id"],  # identifier from geodataframe
    right_on=["fips"],  # identifier from dataframe
)

scheme = mc.Quantiles(df["Median AQI"], k=10)

for y in range(1996, 2025):
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
        gdf[gdf["Year"] == y],
        projection=gcrs.AlbersEqualArea(),
        hue="Median AQI",
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

    plt.title(str(y))

    plt.savefig(f"vis/exports/median_aqi_annual_frames/{y}.png")

#

df["Unhealthiness"] = (
    100
    * (df["Unhealthy Days"] + df["Very Unhealthy Days"] + df["Hazardous Days"])
    / df["Days with AQI"]
)

gdf = geoData.merge(
    df,
    left_on=["id"],  # identifier from geodataframe
    right_on=["fips"],  # identifier from dataframe
)

scheme = mc.Quantiles(
    df["Unhealthiness"],
    k=10,
)

for y in range(1996, 2025):
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
        gdf[gdf["Year"] == y],
        projection=gcrs.AlbersEqualArea(),
        hue="Unhealthiness",
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

    plt.title(str(y))

    plt.savefig(
        f"vis/exports/aqi_unhealthy_percent_total_aqi_days_annual_frames/{y}.png"
    )
