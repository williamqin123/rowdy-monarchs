from matplotlib import pyplot as plt
import sqlite3 as sql
import pandas as pd, numpy as np

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

months_strs = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]
for m in range(12):
    series = []
    xr = np.arange(1996, 2025)
    for y in xr:
        filtered = df[
            (df["date"].dt.month == m)
            & (df["date"].dt.year == y)
            & (df["qty"] < q)  # excludes top 0.1% of entered quantities
        ]
        series.append(filtered["qty"].sum())

    plt.plot(xr, series, label=months_strs[m])

plt.legend()

plt.savefig("vis/exports/sightings_lines.png")

plt.show()
